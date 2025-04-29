# pyTypingGame

A simple typing game implemented using the Pygame library in Python. Test and improve your typing speed and accuracy!

## Features

*   Words fall from the right of the screen.
*   Type the words correctly before they reach the bottom.
*   Score tracking (potential feature, can be added).
*   Increasing difficulty (potential feature, can be added).

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

*   Python 3.x installed on your system. You can download it from [python.org](https://www.python.org/downloads/).
*   `pip` (Python package installer), which usually comes with Python.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/pyTypingGame.git
    cd pyTypingGame
    ```
    *(Replace `your-username` with your actual GitHub username)*

2.  **Create and activate a virtual environment:**

    *   **On Windows:**
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

    *   **On macOS and Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *(Using a virtual environment is recommended to keep dependencies required by different projects separate.)*

3.  **Install dependencies:**
    Make sure your virtual environment is activated. Then, install Pygame:
    ```bash
    pip install pygame
    ```
    *(If you create a `requirements.txt` file later with `pip freeze > requirements.txt`, users can install all dependencies with `pip install -r requirements.txt`)*

### Running the Game

Once the setup is complete and your virtual environment is active, you can run the game:

```bash
python main.py
