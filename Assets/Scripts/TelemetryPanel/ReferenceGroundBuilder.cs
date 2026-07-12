using UnityEngine;

namespace TelemetryPanel
{
    // Hava araci perspektifinden onizleme kamerasinin hareketi
    // algilayabilmesi icin basit bir zemin ve gorsel referans noktalari
    // (landmark) uretir.
    public class ReferenceGroundBuilder : MonoBehaviour
    {
        public float groundSize = 500f;
        public int landmarkCount = 8;
        public float landmarkRadius = 80f;

        void Awake()
        {
            GameObject ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.name = "ReferenceGround";
            ground.transform.SetParent(transform);
            ground.transform.localScale = Vector3.one * (groundSize / 10f);

            for (int i = 0; i < landmarkCount; i++)
            {
                float angle = i * Mathf.PI * 2f / landmarkCount;
                Vector3 pos = new Vector3(Mathf.Cos(angle), 0f, Mathf.Sin(angle)) * landmarkRadius;

                GameObject landmark = GameObject.CreatePrimitive(PrimitiveType.Cube);
                landmark.name = $"Landmark_{i}";
                landmark.transform.SetParent(transform);
                landmark.transform.localPosition = pos + Vector3.up * 2f;
                landmark.transform.localScale = new Vector3(3f, 4f, 3f);
            }
        }
    }
}
