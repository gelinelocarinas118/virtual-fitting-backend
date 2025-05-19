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
    ]);

    /* ───────── 2. Prep directories ─────── */
    $timestamp  = now()->format('Ymd_His');
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

    
public function storeZip(Request $request)
{
    /* ───────── 1. Validate input ───────── */
    $validated = $request->validate([
        'zip'    => 'required|file|mimes:zip',
        'height' => 'required|integer|min:50|max:300',
    ]);

    /* ───────── 2. Prep directories ─────── */
    $timestamp      = now()->format('Ymd_His');
    $baseFolder     = "public/uploads/$timestamp";            
    $extractionPath = storage_path("app/$baseFolder");      
    Storage::makeDirectory($baseFolder);

    /* ───────── 3. Save uploaded ZIP ────── */
    $zipFile     = $validated['zip'];
    $zipRelPath  = $zipFile->storeAs("uploads/$timestamp", 'images.zip', 'public');
    $zipFullPath = storage_path("app/public/$zipRelPath");

    /* ───────── 4. Open + validate ZIP ──── */
    $zip = new \ZipArchive();
    if ($zip->open($zipFullPath) !== true) {
        return response()->json(['error' => 'Failed to open ZIP file.'], 500);
    }

    $frontFiles = $sideFiles = [];
    for ($i = 0; $i < $zip->numFiles; $i++) {
        $stat = $zip->statIndex($i);
        if ($stat === false) continue;
        $name = $stat['name'];
        if (str_ends_with($name, '/')) continue;  

        $lower = strtolower(basename($name));
        if (preg_match('/^front\.(jpg|jpeg|png)$/', $lower)) {
            $frontFiles[] = $name;
        }
        if (preg_match('/^side\.(jpg|jpeg|png)$/', $lower)) {
            $sideFiles[]  = $name;
        }
    }

    if (count($frontFiles) !== 1 || count($sideFiles) !== 1) {
        $zip->close();
        Storage::deleteDirectory($baseFolder);
        return response()->json([
            'error'       => 'ZIP must contain exactly one "front" and one "side" image (jpg/jpeg/png).',
            'front_found' => $frontFiles,
            'side_found'  => $sideFiles,
        ], 422);
    }

    /* ───────── 5. Extract files flat ───── */
    for ($i = 0; $i < $zip->numFiles; $i++) {
        $stat = $zip->statIndex($i);
        if ($stat === false) continue;
        $name = $stat['name'];
        if (str_ends_with($name, '/')) continue;

        $contents = $zip->getFromIndex($i);
        if ($contents === false) {
            $zip->close();
            return response()->json(['error' => "Failed to extract file: $name"], 500);
        }

        $basename = basename($name);
        file_put_contents($extractionPath . DIRECTORY_SEPARATOR . $basename, $contents);
    }
    $zip->close();

    /* ───────── 6. Create DB record ─────── */
    $model = Reconstruction::create([
        'timestamp'      => $timestamp,
        'height_cm'      => $validated['height'],
        'is_saved'       => true,
        'is_processing'  => false,
        'is_model_ready' => false,
        'is_failed'      => false,
        'message'        => 'ZIP extracted (flat, front & side present).',
    ]);

    /* ───────── 7. Notify Flask ─────────── */
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
                'message'     => 'ZIP uploaded, flat-extracted, and sent to Flask.',
                'timestamp'   => $timestamp,
                'height'      => $validated['height'],
                'front_image' => basename($frontFiles[0]),
                'side_image'  => basename($sideFiles[0]),
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