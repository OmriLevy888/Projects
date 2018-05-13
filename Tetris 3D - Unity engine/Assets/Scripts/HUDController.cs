using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class HUDController : MonoBehaviour {

    [SerializeField] GameManager gm;  // a reference to the game manager
    [SerializeField] GameObject mainMenu;  // a reference to the main menu object
    [SerializeField] GameObject gameOver;  // a reference to the game over object
    [SerializeField] Animator scoreAndMultiplierAnimator;  // a reference to the score and multiplier animator component
    [SerializeField] Text score;  // a reference to the score object
    [SerializeField] Text multiplier;  // a reference to the multiplier object
    [SerializeField] Text endScore;  // a reference to the game over screen score text
    [SerializeField] GameObject pauseMenu;  // a reference to the pause menu

    int currScore;  // the current score
    int currMultiplier;  // the current multiplier

    [HideInInspector] public bool playing;  // indicates whether playing at the given moment or not

    void Start() {
        playing = false;

        mainMenu.SetActive(true);  // enabling the main menu

        ResetScoreAndMultiplier();  // reseting the score and multiplier values and texts

        pauseMenu.SetActive(false);  // disabling the pause menu
        gameOver.SetActive(false);  // disabling the game over screen overlay
        scoreAndMultiplierAnimator.gameObject.SetActive(false);  // disabling the score and multiplier object
    }

    void Update() {
        if (Input.GetKeyDown(KeyCode.Escape)) {
            if (playing)
                DisplayPauseMenu();
            else
                UnpauseGame();
        }
    }

    string ScoreToString() {
        if (currScore == 0)
            return "000";

        if (currScore < 10)
            return "00" + currScore;

        if (currScore < 100)
            return "0" + currScore;

        return currScore.ToString();
            
    }

    string MultiplierToString() {
        return "x" + currMultiplier;
    }

    public void ScoreUp(int amount) {
        currScore += amount * currMultiplier;
        
        score.text = ScoreToString();  // update the score text

        scoreAndMultiplierAnimator.Play("ScoreUp");  // play the score up animation
    }

    public void MultiplierUp(int amount) {
        currMultiplier += amount;  // update the multiplier
        currScore += amount * 10;  // update the score

        multiplier.text = MultiplierToString();  // update the multiplier text
        score.text = ScoreToString();  // update the score text

        scoreAndMultiplierAnimator.Play("MultiplierUp");  // play the multiplier up animation
    }

    public void GameOver() {
        scoreAndMultiplierAnimator.enabled = false;  // disabling the score and multiplier animator component
        scoreAndMultiplierAnimator.gameObject.SetActive(false);  // disabling the score and multiplier object

        gameOver.SetActive(true);  // enabling the game over screen overlay
        endScore.text = score.text;  // setting the end score text to the score text

        playing = false;
    }

    public void ResetScoreAndMultiplier() {
        currScore = 0;  // reseting the score
        currMultiplier = 1;  // reseting the multiplier

        score.text = ScoreToString();  // updating the score text
        multiplier.text = MultiplierToString();  // updating the multiplier text
    }

    public void OnPlayAgainPress() {
        gameOver.SetActive(false);  // disables the game over screen overlay
        scoreAndMultiplierAnimator.gameObject.SetActive(true);  // setting the score and multiplier object to active
        scoreAndMultiplierAnimator.enabled = true;  // enabling the score and multiplier animator component
        gm.StartGame();  // restarting the game
        playing = true;
    }

    public void OnPlayPress() {
        mainMenu.SetActive(false);  // disabling the main menu
        gameOver.SetActive(false);  // disables the game over screen overlay
        scoreAndMultiplierAnimator.gameObject.SetActive(true);  // setting the score and multiplier object to active
        scoreAndMultiplierAnimator.enabled = true;  // enabling the score and multiplier animator component
        gm.StartGame();  // restarting the game
        playing = true;
    }

    public void OnQuitButtonPress() {
        Application.Quit();  // quits the application
    }

    public void DisplayPauseMenu() {
        playing = false;  // sets the bool indicating that the game is paused

        Time.timeScale = 0.0f;  // pauses the time

        scoreAndMultiplierAnimator.gameObject.SetActive(false);  // disabling the score and multiplier object
        pauseMenu.SetActive(true);  // displays the pause menu overlay
    }

    public void UnpauseGame() {
        playing = true;  // sets the bool indicating that the game is going on

        Time.timeScale = 1.0f;  // unpauses the time

        scoreAndMultiplierAnimator.gameObject.SetActive(true);  // enabling the score and multiplier object
        pauseMenu.SetActive(false);  // removes the pause menu overlay
    }

    public void OnRestartPress() {
        Time.timeScale = 1.0f;  // unpausing the game

        playing = true;  // setting the bool indicating that the game is going on to true

        pauseMenu.SetActive(false);  // removing the pause menu screen overlay

        scoreAndMultiplierAnimator.gameObject.SetActive(true);  // displaying the score and multiplier screen overlay
        gm.StartGame();  // starting a new game
    }
}
