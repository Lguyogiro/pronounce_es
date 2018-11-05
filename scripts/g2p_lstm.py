import argparse
import numpy as np
import random
from keras.models import Model
from keras.layers import Input, LSTM, Dense

#transcriptions_file = "../corpora/transcriptions_master.txt"

def create_dataset(transcriptions_file):
    lines = [line.strip('\n').split() for line in open(transcriptions_file)]
    untranscribed = []
    input_texts = []
    target_texts = []
    input_chars = set()
    target_chars = set()
    for line in lines:
        if len(line) > 1:
            input_text = line[0]
            target_text = "\t{}\n".format(line[1])
            input_texts.append(input_text)
            target_texts.append(target_text)
            input_chars.update(set(input_text))
            target_chars.update(set(target_text))
        else:
            untranscribed.append(line[0])
    return input_texts, target_texts, input_chars, target_chars, untranscribed


def decode_sequence(input_seq, encoder_model,
                    decoder_model, reverse_target_char_index,
                    num_decoder_tokens, target_token_index,
                    max_decoder_seq_length):

    # Encode the input as state vectors.
    states_value = encoder_model.predict(input_seq)

    # Generate empty target sequence of length 1.
    target_seq = np.zeros((1, 1, num_decoder_tokens))
    # Populate the first character of target sequence with the start character.
    target_seq[0, 0, target_token_index['\t']] = 1.

    # Sampling loop for a batch of sequences
    # (to simplify, here we assume a batch of size 1).
    stop_condition = False
    decoded_sentence = ''
    while not stop_condition:
        output_tokens, h, c = decoder_model.predict(
            [target_seq] + states_value)

        # Sample a token
        sampled_token_index = np.argmax(output_tokens[0, -1, :])
        sampled_char = reverse_target_char_index[sampled_token_index]
        decoded_sentence += sampled_char

        # Exit condition: either hit max length
        # or find stop character.
        if (sampled_char == '\n' or
           len(decoded_sentence) > max_decoder_seq_length):
            stop_condition = True

        # Update the target sequence (of length 1).
        target_seq = np.zeros((1, 1, num_decoder_tokens))
        target_seq[0, 0, sampled_token_index] = 1.

        # Update states
        states_value = [h, c]

    return decoded_sentence


def main(transcriptions_file, interactive=False):
    input_texts, target_texts, input_chars, target_chars, untranscribed = create_dataset(transcriptions_file)
    input_chars = sorted(list(input_chars))
    target_chars = sorted(list(target_chars))
    num_encoder_tokens = len(input_chars)
    num_decoder_tokens = len(target_chars)
    max_encoder_seq_length = max([len(i) for i in input_texts])
    max_decoder_seq_length = max([len(t) for t in target_texts])

    print('Number of samples:', len(input_texts))
    print('Number of unique input tokens:', num_encoder_tokens)
    print('Number of unique output tokens:', num_decoder_tokens)
    print('Max sequence length for inputs:', max_encoder_seq_length)
    print('Max sequence length for outputs:', max_decoder_seq_length)

    batch_size = 64  # Batch size for training.
    epochs = 100  # Number of epochs to train for.
    latent_dim = 256  # Latent dimensionality of the encoding space.
    training_pct = 0.8  # proportion of samples to train on.
    num_samples = int(len(input_texts) * training_pct)  # Number of samples to train on.

    input_token_index = {char: i for i, char in enumerate(input_chars)}
    target_token_index = {char: i for i, char in enumerate(target_chars)}

    encoder_input_data = np.zeros((len(input_texts),
                                   max_encoder_seq_length,
                                   num_encoder_tokens), dtype='float32')
    decoder_input_data = np.zeros((len(input_texts),
                                   max_decoder_seq_length,
                                   num_decoder_tokens), dtype='float32')
    decoder_target_data = np.zeros((len(input_texts),
                                    max_decoder_seq_length,
                                    num_decoder_tokens), dtype='float32')

    for i, (input_text, target_text) in enumerate(zip(input_texts, target_texts)):
        for t, char in enumerate(input_text):
            encoder_input_data[i, t, input_token_index[char]] = 1.
        for t, char in enumerate(target_text):
            # decoder_target_data is ahead of decoder_input_data by one timestep
            decoder_input_data[i, t, target_token_index[char]] = 1.
            if t > 0:
                # decoder_target_data will be ahead by one timestep
                # and will not include the start character.
                decoder_target_data[i, t - 1, target_token_index[char]] = 1.

    # Define an input sequence and process it.
    encoder_inputs = Input(shape=(None, num_encoder_tokens))
    encoder = LSTM(latent_dim, return_state=True)
    encoder_outputs, state_h, state_c = encoder(encoder_inputs)

    # We discard `encoder_outputs` and only keep the states.
    encoder_states = [state_h, state_c]

    # Set up the decoder, using `encoder_states` as initial state.
    decoder_inputs = Input(shape=(None, num_decoder_tokens))

    # We set up our decoder to return full output sequences,
    # and to return internal states as well. We don't use the
    # return states in the training model, but we will use them in inference.
    decoder_lstm = LSTM(latent_dim, return_sequences=True, return_state=True)
    decoder_outputs, _, _ = decoder_lstm(decoder_inputs,
                                         initial_state=encoder_states)
    decoder_dense = Dense(num_decoder_tokens, activation='softmax')
    decoder_outputs = decoder_dense(decoder_outputs)

    # Define the model that will turn
    # `encoder_input_data` & `decoder_input_data` into `decoder_target_data`
    model = Model([encoder_inputs, decoder_inputs], decoder_outputs)

    # Run training
    model.compile(optimizer='rmsprop', loss='categorical_crossentropy')
    model.fit([encoder_input_data, decoder_input_data], decoder_target_data,
              batch_size=batch_size,
              epochs=epochs,
              validation_split=0.2, verbose=2)
    model.save("../models/transcriber.model")

    encoder_model = Model(encoder_inputs, encoder_states)

    decoder_state_input_h = Input(shape=(latent_dim,))
    decoder_state_input_c = Input(shape=(latent_dim,))
    decoder_states_inputs = [decoder_state_input_h, decoder_state_input_c]
    decoder_outputs, state_h, state_c = decoder_lstm(
        decoder_inputs, initial_state=decoder_states_inputs)
    decoder_states = [state_h, state_c]
    decoder_outputs = decoder_dense(decoder_outputs)
    decoder_model = Model(
        [decoder_inputs] + decoder_states_inputs,
        [decoder_outputs] + decoder_states)

    # Reverse-lookup token index to decode sequences back to
    # something readable.
    reverse_input_char_index = dict(
        (i, char) for char, i in input_token_index.items())
    reverse_target_char_index = dict(
        (i, char) for char, i in target_token_index.items())

    if interactive:
        return  # TODO
        # while True:
        #     token = input("Enter a word to be transcribed:\n>>>")

    for seq_index in [random.randint(0, num_samples - 1) for _ in range(10)]:
        # Take one sequence (part of the training test)
        # for trying out decoding.
        input_seq = encoder_input_data[seq_index: seq_index + 1]

        decoded_sentence = decode_sequence(input_seq,
                                           encoder_model,
                                           decoder_model,
                                           reverse_target_char_index,
                                           num_decoder_tokens,
                                           target_token_index,
                                           max_decoder_seq_length)

        print('-')
        print('Input sentence:', input_texts[seq_index])
        print('Decoded sentence:', decoded_sentence)

if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--transcriptions_file', '-t',
                           default="../corpora/transcriptions_master.txt",
                           help=("Path to transcriptions file. "
                                 "File should contain a word and transcription, "
                                 "separated by a space, on each line."))
    argparser.add_argument('-i', '--interactive', action='store_true')
    args = argparser.parse_args()
    main(args.transcriptions_file)


