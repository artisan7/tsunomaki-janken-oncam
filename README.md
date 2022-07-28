<br/>
<p align="center">
  <h3 align="center">Tsunomaki Janken OnCam?</h3>
  
  <p align="center">
    <img src="/assets/screenshot.png" alt="Employee data" title="Employee Data title" width="25%">
  </p>

  <p align="center">
    Play Tsunomaki Janken using your hand's gestures captured on your webcam against an AI opponent ("OnCam" is so fckin lame btw)
    <br/>
    <br/>
  </p>
</p>

![License](https://img.shields.io/github/license/artisan7/tsunomaki-janken-oncam) 

## About The Project

This project was made on-and-off in the span of two weeks. It's sole purpose is for me to test out the mediapipe API before using it in a bigger project.

There are a lot of bugs and I couldn't be bothered to fix them since they're not really important for the main goal of this project (which is just testing the API). Some known issues include:

* The program automatically assumes that there is a webcam. Thus, playing the game without a webcam will result in weird behavior
* There are NO "draw" or "invalid" result screen. In the case of a draw or invalid input (like an unknown gesture or the program failing to detect the hand) it will display a "LOSE" result screen

## Built With



* [mediapipe](https://mediapipe.dev/)
* [pygame](https://www.pygame.org/)

## Getting Started

Make sure you have python 3.x (preferably the latest version) and pip3 before you proceed

### Installation

```sh
git clone https://github.com/artisan7/tsunomaki-janken-oncam.git
```
```sh
pip install -r requirements.txt
```

## Usage

```sh
python main.py
```
NOTE: make sure you have your webcam available. Otherwise, you'll see weird behavior from the app (Yeah I'm too lazy to add error handling stuff)

## License

Distributed under the MIT License. See [LICENSE](https://github.com/artisan7/tsunomaki-janken-oncam/blob/main/LICENSE.md) for more information.
