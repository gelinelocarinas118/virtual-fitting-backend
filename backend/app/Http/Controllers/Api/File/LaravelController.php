<?php

namespace App\Http\Controllers\Api\File;

use App\Http\Controllers\Controller;
use App\Models\Reconstruction;
use Illuminate\Http\Request;


class LaravelController extends Controller
{
    //
       public function reconstructionDone(Request $request){

        // update db status that the model is done for specific timestamp
        // the react expo will periodically checks if the model is ready from its status
        $model = Reconstruction::where('timestamp', $request->timestamp)->first();

        if ($model) {
            $model->update([
                'is_model_ready' => true,
            ]);
        }

    }
}
