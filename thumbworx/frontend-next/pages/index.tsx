import { useState, useEffect } from "react";
import Image from "next/image";
import { Geist, Geist_Mono } from "next/font/google";
import dynamic from "next/dynamic";
import axios from "axios";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

// Dynamically import Map component without SSR
const MapWithNoSSR = dynamic(() => import("../components/Map"), { ssr: false });

// Define type for route data from Flask
interface Route {
  origin: string;
  destination: string;
  created_at?: string;
}

export default function Home() {
  const api = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const [positions, setPositions] = useState([]);
  const [pickupAddress, setPickupAddress] = useState("");
  const [dropoffAddress, setDropoffAddress] = useState("");
  const [formMessage, setFormMessage] = useState("");
  const [routes, setRoutes] = useState<Route[]>([]);

  // Fetch live positions (poll every 5s)
  useEffect(() => {
    const fetchPositions = async () => {
      try {
        const res = await fetch(`${api}/api/traccar/positions`);
        const data = await res.json();
        setPositions(data);
      } catch (err) {
        console.error("Error fetching positions:", err);
      }
    };
    fetchPositions();
    const interval = setInterval(fetchPositions, 5000);
    return () => clearInterval(interval);
  }, [api]);

  // Fetch latest routes from Flask
  const fetchLatestRoutes = async () => {
    try {
      const res = await axios.get<Route[]>("http://127.0.0.1:5000/latest-routes");
      setRoutes(res.data);
    } catch (err) {
      console.error("Error fetching latest routes:", err);
    }
  };

  useEffect(() => {
    fetchLatestRoutes();
  }, []);

  // Submit new route to Flask
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post("http://127.0.0.1:5000/submit-route", {
        origin: pickupAddress,
        destination: dropoffAddress,
      });
      setFormMessage("✅ Route submitted successfully!");
      setPickupAddress("");
      setDropoffAddress("");
      fetchLatestRoutes(); // Refresh list
    } catch (error) {
      console.error("❌ Error submitting route", error);
      setFormMessage("Error sending route request.");
    }
  };

  return (
    <div
      className={`${geistSans.className} ${geistMono.className} font-sans grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20`}
    >
      <main className="flex flex-col gap-[32px] row-start-2 items-center sm:items-start w-full">
        <Image
          className="dark:invert"
          src="/next.svg"
          alt="Next.js logo"
          width={180}
          height={38}
          priority
        />

        {/* SWR Map section */}
        <h1 className="text-xl font-bold">Thumbworx Live Tracking</h1>
        <div className="w-full h-[500px] border rounded-lg overflow-hidden">
          <MapWithNoSSR positions={positions || []} />
        </div>

        {/* Route submission form */}
        <div className="w-full p-4 border rounded-lg bg-gray-50 dark:bg-gray-800">
          <h2 className="text-lg font-semibold mb-2">Submit a Route</h2>
          <form onSubmit={handleSubmit} className="flex flex-col gap-2">
            <input
              type="text"
              value={pickupAddress}
              onChange={(e) => setPickupAddress(e.target.value)}
              placeholder="Pickup address"
              className="p-2 border rounded"
              required
            />
            <input
              type="text"
              value={dropoffAddress}
              onChange={(e) => setDropoffAddress(e.target.value)}
              placeholder="Drop-off address"
              className="p-2 border rounded"
              required
            />
            <button
              type="submit"
              className="bg-blue-500 text-white py-2 rounded hover:bg-blue-600"
            >
              Send Route
            </button>
          </form>
          {formMessage && (
            <p
              className={`mt-2 text-sm ${
                formMessage.startsWith("✅")
                  ? "text-green-600 dark:text-green-400"
                  : "text-red-600 dark:text-red-400"
              }`}
            >
              {formMessage}
            </p>
          )}
        </div>

        {/* Latest routes list */}
        <div className="w-full p-4 border rounded-lg bg-gray-50 dark:bg-gray-800">
          <h2 className="text-lg font-semibold mb-2">Latest Routes</h2>
          {routes.length > 0 ? (
            <ul>
              {routes.map((r, i) => (
                <li key={i}>
                  <strong>{r.origin}</strong> → {r.destination}
                  {r.created_at && (
                    <span className="text-xs text-gray-500">
                      {" "}
                      ({new Date(r.created_at).toLocaleString()})
                    </span>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <p>No routes yet.</p>
          )}
        </div>
      </main>
    </div>
  );
}
