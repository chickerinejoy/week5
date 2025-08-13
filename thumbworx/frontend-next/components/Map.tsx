import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.3/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.3/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.3/images/marker-shadow.png'
});

export default function Map({ positions }: any) {
  const center: [number, number] = [14.5995, 120.9842];
  return (
    <MapContainer center={center} zoom={12} style={{ height: "80vh", width: "100%" }}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {positions.map((p: any, i: number) => (
        <Marker key={i} position={[p.latitude, p.longitude]}>
          <Popup>
            Device {p.deviceId}<br />Speed: {p.speed}
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
