# Stylized Natural Language Generation

The main purpose of this thesis was to create a dialogue system, which is able to generate
text in different styles and control the manifestation of each style.

## Datasets processing
Files run_preparing_lm_data.py and run_preparing_seq2seq_data.py prepare datasets for the model training.

A config for preparing datasets for the **stylized language models**:
```
config = {
    "model_lm_type": 'LSTM',  # GPT2|LSTM
    "feature_based_modifications": False
}
```
Choose the model (GPT2 or LSTM) for what you want prepare datasets. *feature_based_modifications* prepares NIDF metric.

A config for preparing datasets for the **encoder-decoder model**:
```
config = { 
    "dataset_type_seq2seq": 'PERSONA_BOTH',
    "pretraining_dataset": "TWITTER",
    "with_description": True,  # In case PERSONA (with/without persona description)
    # In case of truncating PERSONA data. 0 if it is not needed to be truncated, N if you need to reduce dialogue.
    "context_pair_count": 0,
    "model_seq2seq_type": 'Basemodel'  # BART|Basemodel
}
``` 
**PERSONA_BOTH** represents the whole Persona-Chat dataset. 

**PERSONA** is used for the truncated dataset.

Persona-Chat has descriptions of people, and it is possible to choose whether the generated data set with a description or not (parameter *with_description*).

*context_pair_count* represents the number of last context pairs from the dialogue history. It is used for truncation. For generating the whole dialogue, this parameter should be set to 0.
  
*model_seq2seq_type* is a parameter for choosing the model (BART or Basemodel).

## Models training and testing

A config from *run_lstm_based_model.py*
```
config = {"train_batch_size": 32,
          "embedding_dim": 300,
          "hidden_dim": 512,
          "dropout_rate": 0.1,
          "num_layers": 2,
          "n_epochs": 10,
          "clip": 10,
          "teacher_forcing_ratio": 0.5,
          "style": "funny"  # to train LM model styles: funny|poetic|positive|negative
          }
```
There are parameters only for the stylized language model training. (Before running this script, it is necessary to prepare datasets)

A config from *run_baseline_model.py*
```
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
          "process": 'train',  # train|test
          "is_stylized_generation": True,  # while testing generate text with different styles
          "with_controlling_attributes": True,  # if "is_stylized_generation" is True
          "with_stylized_lm": False,  # if "is_stylized_generation" is True
          "jokes_weight": 0.25,
          "poetic_weight": 0.25,
          "positive_weight": 0.25,
          "negative_weight": 0.25
          }
```
There are parameters for training the baseline model and testing the whole model with weighted decoding or with feature-based modifications.

There are several ways how to compute the score in the Luong attention. In the parameter *attention_model* it is possible to set  
this type (dot/general/concat).

The parameter *decoding_type* represents a decoding strategy during the test time. *weigted_beam* represents a beam search for weighted decoding.

Parameters *beam_width*, *max_sentences*, *max_sentence_len* are used for testing.

To pre-train the baseline model with Twitter data, the parameter *pretraining* should be set to the *True* value.

To train baseline model, based on the pre-trained models, the parameter *with_pretrained_model* should be set to *True* value.

The parameter *process* represents *train* and *test* phases of the model.

The parameter *is_stylized_generation* is set to True, if it is necessary to generate stylized text.

The parameter *with_controlling_attributes* represents feature-based modifications. Specificity control.

The parameter *with_stylized_lm* represents the weighted decoding.

Parameters *jokes_weight*, *poetic_weight*, *positive_weight*, *negative_weight* represents weights of each style for weighted decoding. 

## Installation

This section describes what should be installed to run Baseline model.
To run the pre-trained models such as BART and GPT-2, go to the **bart_gpt** directory. There is a README.md for pre-trained models installation and fine-tuning.

Please install **conda** https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html
for using GPU.
```
pip install -r requirements.txt
```
### Docker 
Installation and running Baseline model with Docker:

(Please check config settings before!)
```
sudo snap install docker

# to train seq2seq model
docker build  -f Dockerfile.train_baseline_seq2seq -t seq2seq .
docker run seq2seq

# to train lm model
docker build  -f Dockerfile.train_baseline_lm -t lm .
docker run lm
```

 

