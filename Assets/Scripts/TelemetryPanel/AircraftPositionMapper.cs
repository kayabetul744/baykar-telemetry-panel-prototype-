using UnityEngine;

namespace TelemetryPanel
{
    // Telemetriden gelen enlem/boylam/irtifa/yon bilgisini, onizleme
    // sahnesindeki hava araci objesinin yerel konum ve rotasyonuna donusturur.
    // Not: gercek bir jeodezik izdusum (UTM vb.) degil, prototip amacli
    // basitlestirilmis, duzlemsel bir yerel donusumdur.
    public class AircraftPositionMapper : MonoBehaviour
    {
        [Header("Bagimliliklar")]
        public TelemetryClient client;
        public Transform aircraftTransform;

        [Header("Referans Nokta (merkez)")]
        public float centerLatitude = 39.9255f;
        public float centerLongitude = 32.8663f;

        [Tooltip("1 derece enlem/boylamin sahnede kac metreye karsilik geldigi")]
        public float metersPerDegree = 111000f;

        [Tooltip("Gercek mesafeyi sahne olcegine sikistirmak icin bolen")]
        public float distanceScaleDivisor = 100f;

        [Tooltip("Gercek irtifayi sahne olcegine sikistirmak icin bolen")]
        public float altitudeScaleDivisor = 20f;

        void OnEnable()
        {
            if (client != null) client.OnTelemetryReceived += HandleTelemetry;
        }

        void OnDisable()
        {
            if (client != null) client.OnTelemetryReceived -= HandleTelemetry;
        }

        void HandleTelemetry(TelemetryData data)
        {
            if (aircraftTransform == null) return;

            float x = (data.longitude - centerLongitude) * metersPerDegree * Mathf.Cos(centerLatitude * Mathf.Deg2Rad) / distanceScaleDivisor;
            float z = (data.latitude - centerLatitude) * metersPerDegree / distanceScaleDivisor;
            float y = data.altitudeMeters / altitudeScaleDivisor;

            aircraftTransform.position = new Vector3(x, y, z);
            aircraftTransform.rotation = Quaternion.Euler(0f, data.headingDegrees, 0f);
        }
    }
}
