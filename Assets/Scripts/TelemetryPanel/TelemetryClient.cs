using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

namespace TelemetryPanel
{
    // Dis sunucudan (mock GCS) UnityWebRequest ile asenkron olarak anlik ucus
    // verisi ceker, JSON'i parse eder ve dinleyicilere (Operator paneli, 3B
    // onizleme haritalayicisi vb.) event olarak iletir.
    public class TelemetryClient : MonoBehaviour
    {
        [Header("Baglanti")]
        public string endpointUrl = "http://localhost:8080/telemetry";
        public float pollIntervalSeconds = 0.5f;
        public float requestTimeoutSeconds = 2f;

        public event Action<TelemetryData> OnTelemetryReceived;
        public event Action<string> OnConnectionError;

        public bool IsConnected { get; private set; }

        void OnEnable()
        {
            StartCoroutine(PollLoop());
        }

        IEnumerator PollLoop()
        {
            var wait = new WaitForSeconds(pollIntervalSeconds);
            while (enabled)
            {
                yield return StartCoroutine(FetchOnce());
                yield return wait;
            }
        }

        IEnumerator FetchOnce()
        {
            using (var request = UnityWebRequest.Get(endpointUrl))
            {
                request.timeout = Mathf.CeilToInt(requestTimeoutSeconds);
                yield return request.SendWebRequest();

                if (request.result != UnityWebRequest.Result.Success)
                {
                    IsConnected = false;
                    OnConnectionError?.Invoke(request.error);
                    yield break;
                }

                TelemetryData data;
                try
                {
                    data = JsonUtility.FromJson<TelemetryData>(request.downloadHandler.text);
                }
                catch (Exception e)
                {
                    IsConnected = false;
                    OnConnectionError?.Invoke($"JSON parse hatasi: {e.Message}");
                    yield break;
                }

                IsConnected = true;
                OnTelemetryReceived?.Invoke(data);
            }
        }
    }
}
