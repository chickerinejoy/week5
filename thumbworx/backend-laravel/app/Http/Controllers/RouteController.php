<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\RouteModel; 
use Carbon\Carbon;

class RouteController extends Controller
{
    public function latestRoutes()
    {
        // Fetch latest routes from DB
        $routes = RouteModel::latest()->take(10)->get();

        // Add computed distance & ETA 
        $routes = $routes->map(function ($route) {
            // Example calculation
            $distanceKm = $this->calculateDistance($route->start_lat, $route->start_lng, $route->end_lat, $route->end_lng);
            $avgSpeedKmH = 40; // Example average speed
            $etaMinutes = round(($distanceKm / $avgSpeedKmH) * 60);

            $route->distance_km = round($distanceKm, 2);
            $route->eta_minutes = $etaMinutes;
            return $route;
        });

        return response()->json($routes);
    }

    private function calculateDistance($lat1, $lon1, $lat2, $lon2)
    {
        $earthRadius = 6371; // in km
        $dLat = deg2rad($lat2 - $lat1);
        $dLon = deg2rad($lon2 - $lon1);

        $a = sin($dLat / 2) * sin($dLat / 2) +
             cos(deg2rad($lat1)) * cos(deg2rad($lat2)) *
             sin($dLon / 2) * sin($dLon / 2);

        $c = 2 * atan2(sqrt($a), sqrt(1 - $a));
        return $earthRadius * $c;
    }
}
