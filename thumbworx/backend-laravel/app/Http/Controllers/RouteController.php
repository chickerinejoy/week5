<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\RouteModel; // make sure this matches your actual model name

class RouteController extends Controller
{
    public function store(Request $request)
{
    try {
        $origin = $request->origin;
        $destination = $request->destination;

        // Store in DB
        $route = RouteModel::create([
            'origin' => $origin,
            'destination' => $destination
        ]);

        return response()->json(['message' => 'Route stored', 'data' => $route]);
    } catch (\Throwable $th) {
        return response()->json(['error' => $th->getMessage()], 500);
    }
}

}
