import tensorflow as tf
from tensorflow.keras.models import Model # type: ignore
from tensorflow.keras.layers import Layer, Input, Dense, Embedding, MultiHeadAttention, LayerNormalization, Dropout # type: ignore
from tensorflow.keras.callbacks import Callback, EarlyStopping, ModelCheckpoint # type: ignore
from tensorflow.keras.preprocessing.sequence import pad_sequences # type: ignore
import numpy as np
import pandas as pd
import os

# Define the transformer block
class TransformerBlock(Layer):
    def __init__(self, embed_dim, num_heads, ff_dim, dropout_rate=0.1):
        super(TransformerBlock, self).__init__()
        self.attention = MultiHeadAttention(num_heads=num_heads, key_dim=embed_dim)
        self.ffn = tf.keras.Sequential([
            Dense(ff_dim, activation='relu'),
            Dense(embed_dim)
        ])
        self.layernorm1 = LayerNormalization(epsilon=1e-6)
        self.layernorm2 = LayerNormalization(epsilon=1e-6)
        self.dropout1 = Dropout(dropout_rate)
        self.dropout2 = Dropout(dropout_rate)

    def call(self, inputs, training=False):
        attn_output = self.attention(inputs, inputs)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.layernorm1(inputs + attn_output)
        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output, training=training)
        return self.layernorm2(out1 + ffn_output)

# Define the transformer model
class TransformerModel(Model):
    def __init__(self, vocab_size, max_len, embed_dim, num_heads, ff_dim, num_layers, dropout_rate=0.1):
        super(TransformerModel, self).__init__()
        self.embedding = Embedding(vocab_size, embed_dim)
        self.positional_encoding = self._get_positional_encoding(max_len, embed_dim)
        self.transformer_blocks = [TransformerBlock(embed_dim, num_heads, ff_dim, dropout_rate) for _ in range(num_layers)]
        self.dropout = Dropout(dropout_rate)
        self.fc = Dense(vocab_size, activation='softmax')

    def _get_positional_encoding(self, max_len, embed_dim):
        pos = np.arange(max_len)[:, np.newaxis]
        i = np.arange(embed_dim)[np.newaxis, :]
        angles = pos / np.power(10000, (2 * (i // 2)) / np.float32(embed_dim))
        angles[:, 0::2] = np.sin(angles[:, 0::2])
        angles[:, 1::2] = np.cos(angles[:, 1::2])
        return tf.constant(angles, dtype=tf.float32)

    def call(self, inputs, training=False):
        x = self.embedding(inputs) + self.positional_encoding[:tf.shape(inputs)[1], :]
        x = self.dropout(x, training=training)
        for block in self.transformer_blocks:
            x = block(x, training=training)
        return self.fc(x)

# Custom Callback for logging
class CustomCallback(Callback):
    def on_epoch_end(self, epoch, logs=None):
        print(f"Epoch {epoch+1}:")
        print(f" - Loss: {logs['loss']:.4f}")
        print(f" - Accuracy: {logs['accuracy']:.4f}")
        print(f" - Val Loss: {logs.get('val_loss', 'N/A'):.4f}")
        print(f" - Val Accuracy: {logs.get('val_accuracy', 'N/A'):.4f}")

# Data preprocessing
def preprocess_data(texts, tokenizer, max_len):
    sequences = tokenizer.texts_to_sequences(texts)
    padded_sequences = pad_sequences(sequences, maxlen=max_len, padding='post')
    return padded_sequences

# Tokenizer and data preparation
class Tokenizer:
    def __init__(self, vocab_size):
        self.tokenizer = tf.keras.preprocessing.text.Tokenizer(num_words=vocab_size, oov_token='<OOV>')
    
    def fit_on_texts(self, texts):
        self.tokenizer.fit_on_texts(texts)
    
    def texts_to_sequences(self, texts):
        return self.tokenizer.texts_to_sequences(texts)
    
    def get_vocab_size(self):
        return len(self.tokenizer.word_index) + 1  # Including the OOV token

# Define parameters
vocab_size = 10000  # Vocabulary size
max_len = 128       # Maximum length of input sequences
embed_dim = 64      # Embedding dimension
num_heads = 8       # Number of attention heads
ff_dim = 128        # Feed-forward dimension
num_layers = 4      # Number of transformer layers
dropout_rate = 0.1  # Dropout rate

# Instantiate the tokenizer and model
tokenizer = Tokenizer(vocab_size)
model = TransformerModel(vocab_size, max_len, embed_dim, num_heads, ff_dim, num_layers, dropout_rate)
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Generate some dummy data for demonstration
def generate_dummy_data(num_samples, max_len, vocab_size):
    texts = [' '.join(np.random.choice(vocab_size, max_len).astype(str)) for _ in range(num_samples)]
    labels = [' '.join(np.random.choice(vocab_size, max_len).astype(str)) for _ in range(num_samples)]
    return texts, labels

num_samples = 1000
texts, labels = generate_dummy_data(num_samples, max_len, vocab_size)

# Prepare data
tokenizer.fit_on_texts(texts)
X_train = preprocess_data(texts, tokenizer, max_len)
y_train = preprocess_data(labels, tokenizer, max_len)
X_val, y_val = X_train[:num_samples // 10], y_train[:num_samples // 10]

# Define callbacks
early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
checkpoint = ModelCheckpoint('transformer_model.h5', save_best_only=True, monitor='val_loss')
custom_callback = CustomCallback()

# Train the model
history = model.fit(X_train, y_train, epochs=10, batch_size=64, validation_data=(X_val, y_val), callbacks=[early_stopping, checkpoint, custom_callback])

# Evaluate the model
eval_results = model.evaluate(X_val, y_val)
print(f"Validation Loss: {eval_results[0]}")
print(f"Validation Accuracy: {eval_results[1]}")

# Load and use the model
