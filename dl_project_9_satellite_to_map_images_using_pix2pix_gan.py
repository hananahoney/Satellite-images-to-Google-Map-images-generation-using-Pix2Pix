# -*- coding: utf-8 -*-
"""DL Project 9. Satellite to map images using Pix2Pix GAN.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/191L6iaN__YByHFqECxj0gIWec8S-UsDi
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras import Model
import os
import glob
import cv2

from PIL import Image

# train_dataset = []
# test_dataset = []

# train_dataset1 = []

# # Load in the images
# for i in range(1096):
#     train_dataset.append(np.array(Image.open(f'maps/train/{i+1}.jpg')))

# for img in train_dataset:
#   satellite_img = img[:256, :256, :]
#   map_img = img[:256, 600:856, :]
#   ls = []
#   ls.append(satellite_img)
#   ls.append(map_img)
#   train_dataset1.append(ls)

# Path to the dataset
dataset_path = 'maps1'

# Function to load and preprocess the images
def load_image(image_file):
    image = tf.io.read_file(image_file)
    image = tf.image.decode_jpeg(image)
    input_image = image[:256, :256, :]
    real_image = image[:256, 600:856, :]

    input_image = tf.cast(input_image, tf.float32)
    real_image = tf.cast(real_image, tf.float32)

    return input_image, real_image

# Function to normalize the images to [-1, 1]
def normalize(input_image, real_image):
    input_image = (input_image / 127.5) - 1
    real_image = (real_image / 127.5) - 1
    return input_image, real_image

# Function to load and preprocess the dataset
def load_image_train(image_file):
    input_image, real_image = load_image(image_file)
    input_image, real_image = normalize(input_image, real_image)
    return input_image, real_image

def load_image_test(image_file):
    input_image, real_image = load_image(image_file)
    input_image, real_image = normalize(input_image, real_image)
    return input_image, real_image

# Creating a TensorFlow dataset
train_dataset = tf.data.Dataset.list_files(os.path.join(dataset_path, 'train/*.jpg'))
train_dataset = train_dataset.map(load_image_train, num_parallel_calls=tf.data.experimental.AUTOTUNE)
train_dataset = train_dataset.shuffle(buffer_size=1000)
train_dataset = train_dataset.batch(1)

test_dataset = tf.data.Dataset.list_files(os.path.join(dataset_path, 'val/*.jpg'))
test_dataset = test_dataset.map(load_image_test)
test_dataset = test_dataset.batch(1)

def build_generator():
  input = layers.Input(shape=(256,256,3), name='input image')
  initializer = tf.random_normal_initializer(0.0,0.02)
  skip = [] #for skiip connections

  # Encoder Part

  result = layers.Conv2D(64, 4, strides=(2,2), padding='same', kernel_initializer=initializer)(input) # 128x12864
  result = layers.LeakyReLU(alpha=0.2)(result)
  skip.append(result)

  result = layers.Conv2D(128, 4, strides=(2,2), padding='same', kernel_initializer=initializer)(result) # 64x64x128
  result = layers.BatchNormalization()(result)
  result = layers.LeakyReLU(alpha=0.2)(result)
  skip.append(result)

  result = layers.Conv2D(256, 4, strides=(2,2), padding='same', kernel_initializer=initializer, use_bias=False)(result) # 32x32x256
  result = layers.BatchNormalization()(result)
  result = layers.LeakyReLU(alpha=0.2)(result)
  skip.append(result)

  result = layers.Conv2D(512, 4, strides=(2,2), padding='same', kernel_initializer=initializer, use_bias=False)(result) # 16x16x512
  result = layers.BatchNormalization()(result)
  result = layers.LeakyReLU(alpha=0.2)(result)
  skip.append(result)

  result = layers.Conv2D(512, 4, strides=(2,2), padding='same', kernel_initializer=initializer, use_bias=False)(result) # 8x8x512
  result = layers.BatchNormalization()(result)
  result = layers.LeakyReLU(alpha=0.2)(result)
  skip.append(result)

  result = layers.Conv2D(512, 4, strides=(2,2), padding='same', kernel_initializer=initializer, use_bias=False)(result) # 4x4x512
  result = layers.BatchNormalization()(result)
  result = layers.LeakyReLU(alpha=0.2)(result)
  skip.append(result)

  result = layers.Conv2D(512, 4, strides=(2,2), padding='same', kernel_initializer=initializer, use_bias=False)(result) # 2x2x512
  result = layers.BatchNormalization()(result)
  result = layers.LeakyReLU(alpha=0.2)(result)
  skip.append(result)

  result = layers.Conv2D(512, 4, strides=(2,2), padding='same', kernel_initializer=initializer, use_bias=False)(result) # 1x1x512
  result = layers.BatchNormalization()(result)
  result = layers.LeakyReLU(alpha=0.2)(result)
  skip.append(result)

  skip = list(reversed(skip[:-1]))

  # Decoder Part

  skip_indx = 0

  result = layers.Conv2DTranspose(512, 4, strides=(2,2), padding='same', kernel_initializer=initializer, use_bias=False)(result) # 2x2x512
  result = layers.BatchNormalization()(result)
  result = layers.Dropout(0.5)(result)
  result = layers.ReLU()(result)
  result = layers.Concatenate()([result,skip[skip_indx]])
  skip_indx += 1

  result = layers.Conv2DTranspose(512, 4, strides=(2,2), padding='same', kernel_initializer=initializer, use_bias=False)(result) # 4x4x512
  result = layers.BatchNormalization()(result)
  result = layers.Dropout(0.5)(result)
  result = layers.ReLU()(result)
  result = layers.Concatenate()([result,skip[skip_indx]])
  skip_indx += 1

  result = layers.Conv2DTranspose(512, 4, strides=(2,2), padding='same', kernel_initializer=initializer, use_bias=False)(result) # 8x8x512
  result = layers.BatchNormalization()(result)
  result = layers.Dropout(0.5)(result)
  result = layers.ReLU()(result)
  result = layers.Concatenate()([result,skip[skip_indx]])
  skip_indx += 1

  result = layers.Conv2DTranspose(512, 4, strides=(2,2), padding='same', kernel_initializer=initializer, use_bias=False)(result) # 16x16x512
  result = layers.BatchNormalization()(result)
  result = layers.ReLU()(result)
  result = layers.Concatenate()([result,skip[skip_indx]])
  skip_indx += 1

  result = layers.Conv2DTranspose(256, 4, strides=(2,2), padding='same', kernel_initializer=initializer, use_bias=False)(result) # 32x32x256
  result = layers.BatchNormalization()(result)
  result = layers.ReLU()(result)
  result = layers.Concatenate()([result,skip[skip_indx]])
  skip_indx += 1

  result = layers.Conv2DTranspose(128, 4, strides=(2,2), padding='same', kernel_initializer=initializer, use_bias=False)(result) # 64x64x128
  result = layers.BatchNormalization()(result)
  result = layers.ReLU()(result)
  result = layers.Concatenate()([result,skip[skip_indx]])
  skip_indx += 1

  result = layers.Conv2DTranspose(64, 4, strides=(2,2), padding='same', kernel_initializer=initializer, use_bias=False)(result) # 128x128x64
  result = layers.BatchNormalization()(result)
  result = layers.ReLU()(result)
  result = layers.Concatenate()([result,skip[skip_indx]])
  skip_indx += 1

  # Last final layer

  result = layers.Conv2DTranspose(3, 4, strides=(2,2), padding='same', activation='tanh', kernel_initializer=initializer, use_bias=False)(result) # 256x256x2

  return Model(inputs=input, outputs=result)

def build_discriminator():
  input = layers.Input(shape=(256,256,3), name="Input image")
  target = layers.Input(shape=(256,256,3), name="Target image")

  initializer = tf.random_normal_initializer(0.0, 0.02)

  merge = layers.Concatenate()([input, target])

  result = layers.Conv2D(64, 4, strides=(2,2), padding='same', kernel_initializer=initializer)(merge) # 128x128x64
  result = layers.LeakyReLU(alpha=0.2)(result)

  result = layers.Conv2D(128, 4, strides=(2,2), padding='same', kernel_initializer=initializer)(result) # 64x64x128
  result = layers.BatchNormalization()(result)
  result = layers.LeakyReLU(alpha=0.2)(result)

  result = layers.Conv2D(256, 4, strides=(2,2), padding='same', kernel_initializer=initializer, use_bias=False)(result) # 32x32x256
  result = layers.BatchNormalization()(result)
  result = layers.LeakyReLU(alpha=0.2)(result)

  result = layers.Conv2D(512, 4, strides=(2,2), padding='same', kernel_initializer=initializer, use_bias=False)(result) # 16x16x512
  result = layers.BatchNormalization()(result)
  result = layers.LeakyReLU(alpha=0.2)(result)

  result = layers.Conv2D(1, 4, strides=(2,2), padding='same', activation='sigmoid', kernel_initializer=initializer, use_bias=False)(result) # # 8x8x1

  return Model(inputs=[input, target], outputs=result)

discriminator_optimizer = tf.keras.optimizers.Adam(2e-4, beta_1=0.5)
discriminator = build_discriminator()
discriminator.compile(loss='binary_crossentropy', optimizer=discriminator_optimizer, metrics=['accuracy'])
discriminator.trainable = False

generator_optimizer = tf.keras.optimizers.Adam(2e-4, beta_1=0.5)
generator = build_generator()
input = layers.Input(shape=(256,256,3))
target = generator(input)
output = discriminator([input, target])

model = Model(inputs=input, outputs=output)

opt = tf.keras.optimizers.Adam(2e-4, beta_1=0.5)
model.compile(loss=['binary_crossentropy','mae'], optimizer=opt, loss_weights=[1,100], metrics=['accuuracy']) # Combination of Binary cross entropy and mean absolute error loss with wieghts 1 and 100 respectively

# This method returns a helper function to compute cross entropy loss
cross_entropy = tf.keras.losses.BinaryCrossentropy(from_logits=True)

def discriminator_loss(real_output, fake_output):
    real_loss = cross_entropy(tf.ones_like(real_output), real_output) # cross_entropy(actual_values, predicted_values)
    fake_loss = cross_entropy(tf.zeros_like(fake_output), fake_output)
    total_loss = real_loss + fake_loss
    return total_loss

def generator_loss(fake_output_disc, gen_image, target):
    loss1 = cross_entropy(tf.ones_like(fake_output_disc), fake_output_disc) # Discriminator loss
    l1_loss = tf.reduce_mean(tf.abs(target - gen_image))
    total_loss = loss1 + (100*l1_loss) # because of weighted losses 1 and 100 mentioned in paper
    return total_loss

import datetime

# Checkpoints
checkpoint_dir = './training_checkpoints'
checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt")
checkpoint = tf.train.Checkpoint(generator_optimizer=generator_optimizer,
                                 discriminator_optimizer=discriminator_optimizer,
                                 generator=build_generator(),
                                 discriminator=build_discriminator())

@tf.function
def train_step(input_image, target, epoch):
    with tf.GradientTape() as gen_tape, tf.GradientTape() as disc_tape:
      gen_output = generator(input_image, training=True)

      disc_real_output = discriminator([input_image, target], training=True)
      disc_fake_output = discriminator([input_image, gen_output], training=True)

      gen_loss = generator_loss(disc_fake_output, gen_output, target)
      disc_loss = discriminator_loss(disc_real_output, disc_fake_output)



    generator_gradients = gen_tape.gradient(gen_loss,
                                            generator.trainable_variables)
    discriminator_gradients = disc_tape.gradient(disc_loss,
                                                 discriminator.trainable_variables)

    generator_optimizer.apply_gradients(zip(generator_gradients,
                                            generator.trainable_variables))
    discriminator_optimizer.apply_gradients(zip(discriminator_gradients,
                                                discriminator.trainable_variables))

def train(train_ds, epochs, test_ds):
    for epoch in range(epochs):

        for input_image, target in train_ds:
            train_step(input_image, target, epoch)

        for inp, tar in test_ds.take(5):
            generate_images(generator, inp, tar)


        if (epoch + 1) % 20 == 0:
            checkpoint.save(file_prefix=checkpoint_prefix)

        print ('Time taken for epoch {} is sec\n'.format(epoch + 1))
    checkpoint.save(file_prefix=checkpoint_prefix)

def generate_images(model, test_input, tar):

    prediction = model.predict(test_input)
    plt.figure(figsize=(15, 15))

    print(prediction[0])
    display_list = [test_input[0], tar[0], prediction[0]]
    title = ['Input Image', 'Ground Truth', 'Generated Image']

    for i in range(3):
        plt.subplot(1, 3, i+1)
        plt.title(title[i])
        plt.imshow(display_list[i] * 0.5 + 0.5)
        plt.axis('off')
    plt.show()

for example_input, example_target in test_dataset.take(1):
    generate_images(generator, example_input, example_target)

EPOCHS = 10
train(train_dataset, EPOCHS, test_dataset)

# !unzip maps1.zip

generator.save("generator.h5")

