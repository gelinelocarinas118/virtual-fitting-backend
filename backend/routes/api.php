<?php

use App\Http\Controllers\Api\Auth\ApiLoginController;
use App\Http\Controllers\Api\Auth\ApiRegisterController;
use App\Http\Controllers\Api\File\UploadController;
use App\Http\Controllers\Api\File\CallbackController;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
|
| Here is where you can register API routes for your application. These
| routes are loaded by the RouteServiceProvider and all of them will
| be assigned to the "api" middleware group. Make something great!
|
*/

Route::post('login', [ApiLoginController::class, 'login']);
Route::post('register', [ApiRegisterController::class, 'register']);

Route::post('upload',[UploadController::class, 'storeZip']);
Route::post('photogrammetry/callback', [CallbackController::class, 'reconstructionDone']);

//test
Route::post('/upload-zip', [UploadController::class, 'storeZip']);

Route::middleware('auth:sanctum')->get('/user', function (Request $request) {
    return $request->user();
});
