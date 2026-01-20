# Teeko AI Project (IA41)

## Project Description

This repository contains the code for our **Artificial Intelligence** (IA41) project focused on creating an AI capable of playing the board game **Teeko**.

Teeko is a simple abstract strategy game played on a 5x5 board. It consists of two phases: piece placement, followed by piece movement. The goal is to align four pieces (in a row, column, diagonal, or a 2x2 square).

The main objective is to develop an efficient decision-making algorithm (such as **Minimax** with and without **Alpha-Beta Pruning**) to allow the computer to play competitively against a human opponent or against itself to compare the efficency of other algorithms.

***

## 🛠️ Installation and Setup

This project is developed using Python.

### Prerequisites

* Python 3.x

### How to Run

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Overnightt/Teeko_IA41.git](https://github.com/Overnightt/Teeko_IA41.git)
    cd Teeko_IA41
    ```
2.  **Execute the main file:**
    ```bash
    python main.py
    ```
    The game will start, allowing you to interact with the AI via the console interface.

***

## 📂 Project Structure

The code is organized around these main files:

* `main.py` : The program's entry point. Manages initialization and the main game loop.
* `plateau.py` : **The User Interface (UI).** Responsible for displaying the board and handling player input/output.
* `game.py` : Contains the core logic for **checking win conditions** and **executing moves** on the board.
* `ia.py` : The heart of the AI. Contains the implementation of the Artificial Intelligence algorithms and the evaluation function.

***

## Tests

This section will be updated with results and data once the performance analysis and strategic tests have been conducted.

### ⏱️ Speed Tests 
This section details the performance comparison between the standard Minmax algorithm and the optimized Minmax with Alpha-Beta Pruning implemented for the Teeko game AI. The goal was to quantify the computational efficiency gained through pruning as the search depth increases. To measure the data I simply computed the average time taken in 5 occurence at each depth.

![alt text](https://github.com/Overnightt/Teeko_IA41/blob/MainV2/Image_for_readme/Bar_chart.png?raw=true)

The results confirm that **Alpha-Beta Pruning significantly improves search speed**, especially at higher depths where the number of possible game states explodes.

