using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PlatformLight : MonoBehaviour {

    Renderer[] platformCubes;
    int currentState;
    Color[] states;

    float intreval;
    bool discoPlatform;

    void Start() {
        platformCubes = gameObject.GetComponentsInChildren<Renderer>();
        currentState = 0;
        states = new Color[] { new Color(1.0f, 0.0f, 0.0f),
                               new Color(1.0f, 0.0f, 1.0f),
                               new Color(0.0f, 0.0f, 1.0f),
                               new Color(0.0f, 1.0f, 1.0f),
                               new Color(0.0f, 1.0f, 0.0f),
                               new Color(1.0f, 1.0f, 0.0f) };
        intreval = 0.5f;
        StartDiscoPlatform();
    }

    public void ChangeColour() {
        int nextState = currentState < states.Length - 1 ? currentState + 1 : 0; 

        Color newColour = states[nextState];

        foreach (Renderer renderer in platformCubes) {
            renderer.material.SetColor("_EmissionColor", newColour);
        }

        currentState = nextState;
    }

    public void StartDiscoPlatform() {
        discoPlatform = true;
        StartCoroutine(DiscoPlatformCoroutine(intreval));
    }

    public void EndDiscoPlatform() {
        discoPlatform = false;
    }

    IEnumerator DiscoPlatformCoroutine(float intreval) {
        float timer = intreval;

        while (discoPlatform) {
            timer -= Time.deltaTime;
            if (timer <= 0.0f) {
                ChangeColour();
                timer = intreval;
            }
            yield return null;
        }
    }
}
