<?php

namespace App\Http\Controllers\api\file;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Storage;
use App\Models\Reconstruction;


class UploadController extends Controller
{

    public function storeImages(Request $request)
    {
        /* ───────── 1. Validate input ───────── */
        $validated = $request->validate([
            'front'  => 'required|image|mimes:jpg,jpeg,png',
            'side'   => 'required|image|mimes:jpg,jpeg,png',
            'height' => 'required|integer|min:50|max:300',
            'timestamp' => 'required|string'
        ]);

        /* ───────── 2. Prep directories ─────── */
        $timestamp  = $validated['timestamp'];
        $baseFolder = "public/uploads/$timestamp";
        Storage::makeDirectory($baseFolder);
        $diskPath   = storage_path("app/$baseFolder");

        /* ───────── 3. Save images ──────────── */
        $frontRel = $validated['front']->storeAs("uploads/$timestamp", 'front.' . $validated['front']->extension(), 'public');
        $sideRel  = $validated['side']->storeAs("uploads/$timestamp", 'side.'  . $validated['side']->extension(),  'public');

        /* ───────── 4. Create DB record ─────── */
        $model = Reconstruction::create([
            'timestamp'      => $timestamp,
            'height_cm'      => $validated['height'],
            'is_saved'       => true,
            'is_processing'  => false,
            'is_model_ready' => false,
            'is_failed'      => false,
            'message'        => 'Images uploaded (front & side).',
        ]);

        /* ───────── 5. Notify Flask ─────────── */
        try {
            $response = Http::post('http://localhost:3001/upload', [
                'timestamp' => $timestamp,
                'height'    => $validated['height'],
            ]);

            if ($response->successful()) {
                $model->update([
                    'is_processing' => true,
                    'message'       => 'Processing started by Flask.',
                ]);

                return response()->json([
                    'message'     => 'Images uploaded and sent to Flask.',
                    'timestamp'   => $timestamp,
                    'height'      => $validated['height'],
                    'front_image' => basename($frontRel),
                    'side_image'  => basename($sideRel),
                    'flask'       => $response->json(),
                ]);
            }

            return response()->json([
                'error' => 'Flask processing failed.',
                'flask' => $response->body(),
            ], 500);
        } catch (\Exception $e) {
            return response()->json([
                'error'     => 'Flask server not reachable.',
                'exception' => $e->getMessage(),
            ], 500);
        }
    }
}
