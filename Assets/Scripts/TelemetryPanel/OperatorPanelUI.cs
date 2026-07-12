using UnityEngine;
using UnityEngine.UI;

namespace TelemetryPanel
{
    // Gelen telemetri paketlerini Canvas UI uzerinde bir IHA yer kontrol
    // istasyonu operator paneli mantigiyla gosterir. Guncelleme, her karede
    // degil, yalnizca yeni bir telemetri paketi geldiginde yapilir (low-latency,
    // gereksiz UI islemi yok).
    public class OperatorPanelUI : MonoBehaviour
    {
        [Header("Bagimliliklar")]
        public TelemetryClient client;

        [Header("Metin Alanlari")]
        public Text aircraftIdText;
        public Text positionText;
        public Text altitudeText;
        public Text speedText;
        public Text headingText;
        public Text statusText;
        public Text lastUpdateText;

        [Header("Gorseller")]
        public RectTransform headingNeedle;
        public Image linkStatusIndicator;
        public Image batteryFill;

        public Color connectedColor = Color.green;
        public Color disconnectedColor = Color.red;

        void OnEnable()
        {
            if (client == null) return;
            client.OnTelemetryReceived += HandleTelemetry;
            client.OnConnectionError += HandleError;
        }

        void OnDisable()
        {
            if (client == null) return;
            client.OnTelemetryReceived -= HandleTelemetry;
            client.OnConnectionError -= HandleError;
        }

        void HandleTelemetry(TelemetryData data)
        {
            if (aircraftIdText != null) aircraftIdText.text = data.aircraftId;
            if (positionText != null) positionText.text = $"{data.latitude:0.0000}, {data.longitude:0.0000}";
            if (altitudeText != null) altitudeText.text = $"{data.altitudeMeters:0.0} m";
            if (speedText != null) speedText.text = $"{data.speedKmh:0.0} km/h";
            if (headingText != null) headingText.text = $"{data.headingDegrees:0.0} deg";
            if (statusText != null) statusText.text = data.status;
            if (lastUpdateText != null) lastUpdateText.text = $"Son guncelleme: {System.DateTime.Now:HH:mm:ss}";

            if (headingNeedle != null) headingNeedle.localEulerAngles = new Vector3(0f, 0f, -data.headingDegrees);
            if (batteryFill != null) batteryFill.fillAmount = Mathf.Clamp01(data.batteryPercent / 100f);
            if (linkStatusIndicator != null) linkStatusIndicator.color = connectedColor;
        }

        void HandleError(string message)
        {
            if (statusText != null) statusText.text = $"BAGLANTI HATASI: {message}";
            if (linkStatusIndicator != null) linkStatusIndicator.color = disconnectedColor;
        }
    }
}
