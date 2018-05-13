using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

public class PieceController : MonoBehaviour {

    enum Dir { None = 0, Up = 1, Right = 2, Down = -1, Left = -2 }

    [SerializeField] GameObject checkCubes;
    [SerializeField] LayerMask cubeMask;
    Transform[] checkCubesObjects;

    [SerializeField] KeyCode drop = KeyCode.LeftShift;  // drop by one
    [SerializeField] KeyCode fullDrop = KeyCode.Tab;  // drop as much as possible

    [SerializeField] KeyCode moveUp = KeyCode.W;  // move forwards from the camera's perspective
    [SerializeField] KeyCode moveLeft = KeyCode.A;  // move left from the camera's perspective
    [SerializeField] KeyCode moveDown = KeyCode.S;  // move backwards from the camera's perspective
    [SerializeField] KeyCode moveRight = KeyCode.D;  // move right from the camera's perspective

    [SerializeField] KeyCode rotateUp = KeyCode.UpArrow;  // rotate forwards from the camera's perspective
    [SerializeField] KeyCode rotateLeft = KeyCode.LeftArrow;  // rotate to the left from the camera's perspective
    [SerializeField] KeyCode rotateDown = KeyCode.DownArrow;  // rotate backwards from the camera's perspective
    [SerializeField] KeyCode rotateRight = KeyCode.RightArrow;  // rotate to the right from the camera's perspective

    [HideInInspector] public int id;  // the id of this piece
    [HideInInspector] public GameManager gm;  // reference to the GameManger

    public float FallTime;  // amount of time between each drop
    [HideInInspector] public bool Falling;  // indicates whether the object is falling

    Camera playerCamera;
    float fallCounter;

    bool moveable;
    [SerializeField] float maxMovableCounter;
    float moveableCounter;

    int cubes;
    [HideInInspector] public PlatformLight Platform;

    float lastChanceTime = 0.625f;  // the window of time to move the piece after it has landed

    [HideInInspector] public HUDController hud;  // a reference to the hud

    public void DecrementCubes() {
        cubes--;

        if (cubes == 0)
            Destroy(gameObject);
    }

    void Awake() {
        playerCamera = Camera.main;

        fallCounter = FallTime;
        Falling = true;

        cubes = gameObject.GetComponentsInChildren<Cube>().Length;

        checkCubesObjects = checkCubes.GetComponentsInChildren<Transform>();

        moveable = true;
        moveableCounter = 0.0f;
    }

	void Update() {
        if (!hud.playing)
            return;

        if (!Falling && moveable) {
            moveableCounter -= Time.deltaTime;

            if (moveableCounter <= 0.0f) {
                moveable = false;
                AddToLayers();
            }
        }

        if (Falling) {  // if the cube is falling
            fallCounter -= Time.deltaTime;  // advance the timer

            if (fallCounter <= 0.0f) {  // if should drop
                Descend();
                fallCounter = FallTime;  // reset the timer
            }

            if (Input.GetKeyDown(drop)) {
                Descend();  // descend
            } else if (Input.GetKeyDown(fullDrop)) {
                FullDescend();  // descend as much as possible
            }
        }

        if (moveable) {
            if (Input.GetKeyDown(moveUp)) {
                MovePiece(Dir.Up);  // move up
            } else if (Input.GetKeyDown(moveLeft)) {
                MovePiece(Dir.Left);  // move left
            } else if (Input.GetKeyDown(moveDown)) {
                MovePiece(Dir.Down);  // move down
            } else if (Input.GetKeyDown(moveRight)) {
                MovePiece(Dir.Right);  // move right
            }

            if (Input.GetKeyDown(rotateUp)) {
                RotatePiece(Dir.Up);  // rotate up
            } else if (Input.GetKeyDown(rotateLeft)) {
                RotatePiece(Dir.Left);  // rotate left
            } else if (Input.GetKeyDown(rotateDown)) {
                RotatePiece(Dir.Down);  // rotate down
            } else if (Input.GetKeyDown(rotateRight)) {
                RotatePiece(Dir.Right);  // rotate right
            }
        }
    }

    public bool CanDescend(float amount = 1) {
        if (!ValidTransform(Vector3.down * amount, Vector3.zero))
            return false;

        foreach (Transform checkCube in checkCubesObjects)
            if (checkCube.position.y < amount + 0.5f)
                return false;

        return true;
    }

    void Descend() {
        if (CanDescend()) {  // if can descend
            transform.Translate(Vector3.down, Space.World);  // descned
            Platform.ChangeColour();  // change the platform lights
        } else {
            Falling = false;
            StartCoroutine(Blink());
        }
    }

    public IEnumerator Blink() {
        float timer = lastChanceTime;
        Renderer[] children = GetComponentsInChildren<Renderer>();

        if (children.Length == 0)
            timer = -1.0f;

        Color originalColour = children[0].material.GetColor("_EmissionColor");
        Color finalColour = new Color(1.0f, 1.0f, 1.0f, 1.0f);
        Color newColour = new Color();
        float percent = 0.0f;
        float oneMinusPercent = 1.0f;

        while (timer > 0.0f) {
            if (timer > lastChanceTime / 2.0f) {
                percent = (timer - (lastChanceTime / 2.0f)) / (lastChanceTime / 2.0f);
                oneMinusPercent = 1.0f - percent;
                newColour = new Color(percent * originalColour.r + oneMinusPercent * finalColour.r, 
                                      percent * originalColour.g + oneMinusPercent * finalColour.g, 
                                      percent * originalColour.b + oneMinusPercent * finalColour.b, 
                                      percent * originalColour.a + oneMinusPercent * finalColour.a);
            } else {
                percent = ((lastChanceTime / 2.0f) - timer) / (lastChanceTime / 2.0f);
                oneMinusPercent = 1.0f - percent;
                newColour = new Color(percent * originalColour.r + oneMinusPercent * finalColour.r,
                                      percent * originalColour.g + oneMinusPercent * finalColour.g,
                                      percent * originalColour.b + oneMinusPercent * finalColour.b,
                                      percent * originalColour.a + oneMinusPercent * finalColour.a);
            }

            foreach (Renderer renderer in children)
                renderer.material.SetColor("_EmissionColor", newColour);

            timer -= Time.deltaTime;
            yield return null;
        }
    }

    void FullDescend() {
        if (CanDescend()) {
            float amount = 1;

            while (CanDescend(amount + 1))
                amount++;

            transform.Translate(Vector3.down * amount, Space.World);

            Platform.ChangeColour();

            Falling = false;
            StartCoroutine(Blink());
        }
    }

    void MovePiece(Dir dir) {
        Vector3 movementDir;

        if (playerCamera.GetComponent<CameraControl>().Arial && (dir == Dir.Up || dir == Dir.Down)) {  // if in ariel view and moving up or down
            movementDir = playerCamera.transform.up * (float)dir / Math.Abs((float)dir);
        } else if (dir == Dir.Up || dir == Dir.Down) {  // if moving up or down
            movementDir = playerCamera.transform.forward * (float)dir / Math.Abs((float)dir);
        } else {  // if moving left or right
            movementDir = playerCamera.transform.right * (float)dir / Math.Abs((float)dir);
        }

        if (ValidTransform(movementDir, Vector3.zero))
            transform.position += movementDir;
    }

    void RotatePiece(Dir dir) {
        Vector3 rotation;

        if (dir == Dir.Up || dir == Dir.Down) {  // if rotating up or down
            rotation = playerCamera.transform.right * 90.0f * (float)dir / Math.Abs((float)dir);
        } else {  // if rotating left or right
            rotation = playerCamera.transform.up * 90.0f * (float)dir / Math.Abs((float)dir);
        }

        if (ValidTransform(Vector3.zero, rotation))
            transform.Rotate(rotation, Space.World);
    }

    public bool ValidTransform(Vector3 position, Vector3 rotation) {
        Vector3 a = new Vector3(checkCubes.transform.position.x, checkCubes.transform.position.y, checkCubes.transform.position.z);
        Vector3 b = new Vector3(checkCubes.transform.eulerAngles.x, checkCubes.transform.eulerAngles.y, checkCubes.transform.eulerAngles.z);

        

        checkCubes.transform.position = checkCubes.transform.position + position;
        if (rotation != Vector3.zero)
            checkCubes.transform.Rotate(rotation, Space.World);

        bool valid = true;

        foreach (Transform checkCube in checkCubesObjects) {
            // check if out of the platform
            if (checkCube.position.x > 2.5f || checkCube.position.x < -2.5f || checkCube.position.z > 2.5f || checkCube.position.z < -2.5f) {
                valid = false;
                break;
            }

            // check if colliding with another piece
            Collider[] hits = Physics.OverlapSphere(checkCube.transform.position, 0.25f, cubeMask);

            foreach (Collider hit in hits) {
                if (hit.GetComponent<Cube>().ID != id) {
                    valid = false;
                    break;
                }
                    
            }
        }

        checkCubes.transform.position = a;  // restoring the position
        checkCubes.transform.rotation = Quaternion.Euler(b);  // restoring the rotation

        return valid;
    }

    public void AddToLayers() {
        // for all the children of this object, get the ones that have a renderer component, for all of them, get the ones whose tag is "Cube", and get the
        // game objects each of those are on
        foreach (GameObject cube in gameObject.GetComponentsInChildren<Renderer>().Where(r => r.tag == "Cube").Select(r => r.gameObject)) {
            gm.AddCubeToLayer(cube);  // add the current cube to a layer
        }

        gm.SpawnPiece();  // spawn the next piece
    }
}
