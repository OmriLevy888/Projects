using System.Collections.Generic;
using UnityEngine;

public class GameManager : MonoBehaviour {

    [SerializeField] HUDController hud;  // reference to the hud

    [SerializeField] GameObject spawnLoc;  // the spawn location
    [SerializeField] GameObject platform;  // the platform
    [SerializeField] PlatformLight pl;  // a reference to the platform lights

    [SerializeField] GameObject[] prefabs;  // prefabs of the pieces
    [SerializeField] Material[] materials;  // the materials for the pieces
    [SerializeField] Transform pieces;  // a parent object to group the pieces

    [SerializeField] float maxFallTime;  // the maximum time for the piece to fall
    [SerializeField] float minFallTime;  // the minimum time for the piece to fall

    Vector3[] spawnLocs;  // internal spawn locations

    Transform[] platformParts;  // internal platform parts

    GameObject currentPiece;  // the current piece
    HashSet<PieceController> platformPieces;  // all the pieces that are on the platform
    HashSet<GameObject>[] cubeLayers;  // all the cubes that are on the platform
    int id;  // the id of the current cube

    bool gameOver;  // indicates whther the game is over or not 

    void Start() {
        gameOver = true;
    }

    public void StartGame() {
        pl.EndDiscoPlatform();  // stops the disco platform

        hud.ResetScoreAndMultiplier();  // resets the score nad multiplier on the hud

        foreach (PieceController piece in pieces.GetComponentsInChildren<PieceController>())  // for all of the already spawn pieces
            Destroy(piece.gameObject);  // delete the piece

        platformParts = platform.GetComponentsInChildren<Transform>();  // gets all the platform parts
        spawnLocs = new Vector3[platformParts.Length];

        for (int i = 0; i < platformParts.Length; i++) {
            spawnLocs[i] = new Vector3(platformParts[i].position.x, 8.0f, platformParts[i].position.z);  // sets the spawn locations 
        }

        platformPieces = new HashSet<PieceController>();
        cubeLayers = new HashSet<GameObject>[7];
        for (int i = 0; i < cubeLayers.Length; i++)
            cubeLayers[i] = new HashSet<GameObject>();
        id = 0;
        gameOver = false;  // sets the game stat to running
        SpawnPiece(false);  // spawns the first piece
    }

    public void SpawnPiece(bool score = true) {
        if (gameOver)  // if the game is already over
            return;  // do not spawn a piece

        System.Random rng = new System.Random();  // instantiate a pseudo random number generator

        int choice = rng.Next(0, prefabs.Length);  // getting a random piece
        currentPiece = Instantiate(prefabs[choice], pieces);  // spawning a random piece

        while (true) {  // as long as a valid position and a valid rotation have not been chosen
            currentPiece.transform.position = Vector3.zero;  // setting the position to zero
            currentPiece.transform.eulerAngles = Vector3.zero;  // setting the rotation to zero

            choice = rng.Next(0, spawnLocs.Length);
            Vector3 pos = spawnLocs[choice];  // getting a random spawn location
            Vector3 rot = new Vector3(90.0f * rng.Next(-3, 3), 90.0f * rng.Next(-3, 3), 90.0f * rng.Next(-3, 3));  // getting a random spawn rotation

            if (currentPiece.GetComponent<PieceController>().ValidTransform(pos, rot)) {  // if the location and rotation are valid
                currentPiece.transform.position = pos;  // moving the piece to a random spawn point
                currentPiece.transform.eulerAngles = rot;  // setting the piece with a random rotation
                currentPiece.GetComponent<PieceController>().id = id;  // setting the id of the piece to the current id
                currentPiece.GetComponent<PieceController>().gm = this;  // setting the piece's GameManager reference
                currentPiece.GetComponent<PieceController>().FallTime = CalcFallTime();  // setting the piece's fall intreval
                currentPiece.GetComponent<PieceController>().hud = hud;  // setting the piece's hud reference

                break;  // stop the loop
            }
        }

        currentPiece.GetComponent<PieceController>().Platform = platform.GetComponent<PlatformLight>();

        choice = rng.Next(0, materials.Length);

        foreach (Renderer rend in currentPiece.GetComponentsInChildren<Renderer>())
            rend.material = materials[choice];  // setting the cubes' colour

        foreach (Cube cb in currentPiece.GetComponentsInChildren<Cube>())
            cb.ID = id;  // setting the cubes' id

        if (score) {  // if should advance the score and check for complete layers
            hud.ScoreUp(currentPiece.GetComponentsInChildren<Cube>().Length);
            RemoveLayers();
        }
        
        id++;  // increment the id
    }

    float CalcFallTime() {
        // the function for calculating the fall time f(x) = x ^ 2  / 2 * x ^ 1.75
        if (id == 0)  // if on the first piece (id = 0)
            return maxFallTime;  // return the maximum fall intreval
        float ret = Mathf.Pow(id, 2) / Mathf.Pow(2 * id, 1.75f);  // calculating the difference
        ret = Mathf.Clamp(ret, minFallTime, maxFallTime);  // calmping the value
        return maxFallTime - ret;  // returning the fall intreval
    }

    public void AddCubeToLayer(GameObject go) {
        int layer = (int)Mathf.Ceil(go.transform.position.y - platform.transform.position.y) - 1;

        if (layer >= cubeLayers.Length) {
            GameOver();
            return;
        }

        cubeLayers[layer].Add(go);    // adding the cube to the platform cubes
        platformPieces.Add(go.GetComponentInParent<PieceController>());  // adding the piece to the platform pieces
    }

    void GameOver() {
        gameOver = true;  // set the game state to over
        hud.GameOver();  // play the game over animation
        pl.StartDiscoPlatform();  // starts the disco platform
    }

    void RemoveLayers() {
        List<int> completeLayers = FindCompleteLayers();

        if (completeLayers.Count == 0)
            return;

        foreach (int i in completeLayers) {
            foreach (GameObject cube in cubeLayers[i]) { // for all of the completed layer
                Destroy(cube);  // destroy all the cubes from the current completed layer
                cube.GetComponentInParent<PieceController>().DecrementCubes();
            }
            cubeLayers[i].Clear();  // clear the set representing the current completed layer
        }

        for (int a = 0; a < completeLayers.Count; a++) {  // for all of the complete layers
            for (int i = 0; i < cubeLayers.Length; i++) {  // for all of the not complete layers
                if (cubeLayers[i].Count > 0) {  // if the current layer is not empty
                    for (int j = 0; j < i; j++) {  // for all of the layers under the current not complete layers
                        if (cubeLayers[j].Count == 0) { // if the layer is empty
                            foreach (GameObject cube in cubeLayers[i]) {  // for all of the cubes in the current not complete layer
                                cube.transform.Translate(Vector3.down, Space.World);  // move the cube down
                            }
                            Swap(cubeLayers, i, j);  // move the uncomplete layer one layer down
                        }
                    }

                    
                }
            }
        }

        hud.MultiplierUp(completeLayers.Count);  // increment the multiplier
    }

    void Swap<T>(IList<T> i, int a, int b) {
        T temp = i[a];
        i[a] = i[b];
        i[b] = temp;
    }

    List<int> FindCompleteLayers() {
        List<int> retVal = new List<int>();

        for (int i = 0; i < cubeLayers.Length; i++) {
            if (cubeLayers[i].Count == platformParts.Length - 1)
                retVal.Add(i);
        }

        return retVal;
    }
}
