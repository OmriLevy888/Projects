using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Cube : MonoBehaviour {

    public int ID;  // the piece's id

    PieceController piece;  // reference to the piece

    void Start() {
        piece = gameObject.GetComponentInParent<PieceController>();
    }

    void OnTriggerEnter(Collider collider) {
        if (piece == null)
            return;

        if (!piece.Falling)
            return;

        if (transform.position.y < 1.5f || CubeCollide(collider)) {  // if collided with the platform or with another piece
            piece.Falling = false;  // stop the movement and spawn another piece
            StartCoroutine(piece.Blink());
        } 
    }

    bool CubeCollide(Collider collider) {
        if (collider.tag != "Cube")  // checks that collided with a cube
            return false;

        Vector3 colliderPosition = collider.transform.position;
        Vector3 currPos = transform.position;

        bool sameX = Mathf.Abs(colliderPosition.x - currPos.x) < 0.1f;  // checks that the cubes have the same x value
        bool sameZ = Mathf.Abs(colliderPosition.z - currPos.z) < 0.1f;  // checks that the cubes have the same z value
        bool lowerY = colliderPosition.y - currPos.y < 0.5f;  // checks that the other cube is lower than this cube
        bool inPlace = sameX && sameZ && lowerY;  // checks that the cube is directly above the other cube 

        bool differentPiece = collider.gameObject.GetComponent<Cube>().ID != ID;  // checks that the cubes belong to different pieces

        return differentPiece && inPlace;  // returns true if collided with a cube from a different piece and is directly above the other cube
    }
}
