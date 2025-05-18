<?php

namespace App\Http\Controllers\file;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\Reconstruction;

class CallbackController extends Controller
{
    public function reconstructionDone(Request $request){
     
        // update db status that the model is done for specific timestamp
        // the react expo will periodically checks if the model is ready from its status
        $model = Reconstruction::where('timestamp', $request->timestamp)->first();

        if ($model && $model->message === 'Success') {
            $model->update([
                'is_model_ready' => true,
            ]);
        }

    }
}
