<?php

namespace App\Models;

use Backpack\CRUD\app\Models\Traits\CrudTrait;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Tags extends Model
{
    use CrudTrait;
    use HasFactory;

    protected $table = 'tags';
    protected $guarded = ['id'];
    protected $fillable = ['name', 'slug'];

    public function goodHistories()
    {
        return $this->belongsToMany(GoodHistories::class);
    }
}