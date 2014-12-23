Missing Word Locator
================

# Introduction

This is a missing word locator using Kaggle's Billion Word Imputation dataset, located here:

https://www.kaggle.com/c/billion-word-imputation/data

We originally modeled this project to be a full submission for the Billion Word Imputation challenge, 
but the challenge of both predicting the word's location and what word it was proved to
be very taxing on our computational resources and time. Instead, we chose to focus on the
problem of locating the missing word within a sentence. We use two methods to predict the
location of the missing word:

1. Averaged perceptron using brown clustering to cluster words, and n-grams as features
2. Markov chains using long-distance bigrams

We find that the success rate of averaged perceptron peaks at about 50%, and the markov chain model 30%.