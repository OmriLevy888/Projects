using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CameraControl : MonoBehaviour {

    [SerializeField] KeyCode left;  // a key to rotate left
    [SerializeField] KeyCode right;  // a key to rotate right
    [SerializeField] KeyCode arialView;  // a key for arial view
    [SerializeField] float rotAmount;  // the amount to rotate per turn

    [SerializeField] float distance;  // the distance from the anchor point
    [SerializeField] Vector3 anchorPoint;  // the anchor point to rotate around

    enum RotDir { None = 0, Left = 1, Right = -1 }  // rotation directions

    float yPos;  // the y position when not in arial view

    int curr;  // the current position
    Vector2[] positions;  // all the camera positions

    [HideInInspector] public bool Arial;  // indicates whether in arial view or not

    GameObject mainLight;  // a reference to the light

    void Start() {
        yPos = transform.position.y;

        curr = 0;  // setting the current camera position to 0
        positions = new Vector2[4];  // initializing the camera positions
        positions[0] = new Vector2(0.0f, -distance);
        positions[1] = new Vector2(-distance, 0.0f);
        positions[2] = new Vector2(0.0f, distance);
        positions[3] = new Vector2(distance, 0.0f);

        transform.position = new Vector3(positions[curr].x + anchorPoint.x, transform.position.y, positions[curr].y + anchorPoint.z);  // setting the initial camera position

        Arial = false;  // setting arial view to false

        mainLight = GetComponentInChildren<Light>().gameObject;  // setting the light
        mainLight.transform.LookAt(anchorPoint);  // rotating the light towards the platform
    }

    void LateUpdate() {
        if (Input.GetKeyDown(left)) {  // if pressed the left rotate key
            RotateCameraSteps(RotDir.Left);  // rotate left
        } else if (Input.GetKeyDown(right)) {  // if pressed the right rotate key
            RotateCameraSteps(RotDir.Right);  // rotate right
        } else if (Input.GetKeyDown(arialView) || Input.GetKeyUp(arialView))  // if presesd the arial view switch key
            SwitchArialView();  // switch arial view

    }

    void RotateCameraSteps(RotDir dir) {
        if (Arial)
            return;

        Vector3 currRot = transform.rotation.eulerAngles;  // get current rotation
        currRot.y += (float)dir * rotAmount;  // apply rotation
        transform.rotation = Quaternion.Euler(currRot);  // set new rotation

        curr += (int)dir;  // updating the current position
        curr = curr == positions.Length ? 0 : curr == -1 ? positions.Length - 1 : curr;  // moving between the max position and the minimum position

        transform.position = new Vector3(positions[curr].x + anchorPoint.x, yPos, positions[curr].y + anchorPoint.z);  // setting the position of the camera

        mainLight.transform.LookAt(anchorPoint);  // rotation the light to face the platform
    }

    void SwitchArialView() {
        Arial = !Arial;  // switch view mode

        if (Arial) {  // if switched to aial
            transform.position = new Vector3(anchorPoint.x, anchorPoint.y + 12.0f, anchorPoint.z);  // set the camera to be above the platform

            transform.LookAt(anchorPoint);  // set the camera to look at the platform
            mainLight.transform.LookAt(anchorPoint);  // set the light to face the platform
        } else {  // if switched from arial
            transform.position = new Vector3(positions[curr].x + anchorPoint.x, yPos, positions[curr].y + anchorPoint.z);  // set the camera to the current position

            transform.LookAt(new Vector3(anchorPoint.x, yPos, anchorPoint.z));  // set the camera to look at a point above the platform
            mainLight.transform.LookAt(anchorPoint);  // set the light to face the platform
        }
    }
}