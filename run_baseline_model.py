from processes import run_model

config = {"train_batch_size": 32,
          "embedding_dim": 300,
          "hidden_dim": 512,
          "dropout_rate": 0.1,
          "num_layers": 2,
          "n_epochs": 10,
          "clip": 10,
          "teacher_forcing_ratio": 0.1,
          "with_attention": True, 
          "attention_model": 'concat',  # dot|general|concat
          "decoding_type": 'beam',  # beam|greedy|weighted_beam
          "beam_width": 4,
          "max_sentences": 3,  # number of generated sentences by beam decoding
          "max_sentence_len": 40,  # max length of a sentence generated by beam decoding
          "pretraining": True,  # it's necessary to prepare TWITTER data before
          "with_pretrained_model": True,  # to train a model with pretrained model
          "process": 'test',  # train|test
          "is_stylized_generation": True,  # while testing generate text with different styles
          "with_controlling_attributes": True,  # if "is_stylized_generation" is True
          "with_stylized_lm": False,  # if "is_stylized_generation" is True
          "baseline_weight": 0.2,
          "jokes_weight": 0.2,
          "poetic_weight": 0.2,
          "positive_weight": 0.2,
          "negative_weight": 0.2
          }

if __name__ == "__main__":
    run_model(config)
