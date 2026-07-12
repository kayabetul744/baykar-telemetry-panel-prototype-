namespace TelemetryPanel
{
    // Mock GCS sunucusundan gelen JSON telemetri paketiyle bire bir eslesen,
    // JsonUtility uyumlu duz veri sinifi.
    [System.Serializable]
    public class TelemetryData
    {
        public string aircraftId;
        public string timestampUtc;
        public float latitude;
        public float longitude;
        public float altitudeMeters;
        public float speedKmh;
        public float headingDegrees;
        public float batteryPercent;
        public string status;
        public float linkQuality;
    }
}
