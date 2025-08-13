<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;


class TraccarController extends Controller
{
    public function devices()
    {
        $res = Http::withBasicAuth(env('TRACCAR_USER'), env('TRACCAR_PASS'))
            ->get(env('TRACCAR_BASE_URL').'/api/devices');
        return response()->json($res->json());
    }

    public function positions()
    {
        $res = Http::withBasicAuth(env('TRACCAR_USER'), env('TRACCAR_PASS'))
            ->get(env('TRACCAR_BASE_URL').'/api/positions');
        return response()->json($res->json());
    }
}