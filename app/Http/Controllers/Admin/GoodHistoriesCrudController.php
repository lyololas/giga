<?php

namespace App\Http\Controllers\Admin;

use Backpack\CRUD\app\Http\Controllers\CrudController;
use App\Http\Requests\GoodHistoriesRequest;
use App\Models\Tag;

class GoodHistoriesCrudController extends CrudController
{
    use \Backpack\CRUD\app\Http\Controllers\Operations\ListOperation;
    use \Backpack\CRUD\app\Http\Controllers\Operations\CreateOperation;
    use \Backpack\CRUD\app\Http\Controllers\Operations\UpdateOperation;
    use \Backpack\CRUD\app\Http\Controllers\Operations\DeleteOperation;
    use \Backpack\CRUD\app\Http\Controllers\Operations\ShowOperation;

    public function setup()
    {
        $this->crud->setModel(\App\Models\GoodHistories::class);
        $this->crud->setRoute(config('backpack.base.route_prefix') . '/good-histories');
        $this->crud->setEntityNameStrings('good history', 'good histories');
    }

    protected function setupListOperation()
    {
        $this->crud->addColumn([
            'name' => 'title',
            'label' => 'Title',
        ]);
        
        $this->crud->addColumn([
            'name' => 'user_id',
            'label' => 'Author',
            'type' => 'select',
            'entity' => 'user',
            'attribute' => 'name',
        ]);
        
        $this->crud->addColumn([
            'name' => 'is_moderated',
            'label' => 'Moderated',
            'type' => 'boolean',
        ]);
    }

    protected function setupCreateOperation()
    {
        $this->crud->setValidation(GoodHistoriesRequest::class);

        $this->crud->addField([
            'name' => 'title',
            'label' => 'Title',
            'type' => 'text',
        ]);

        $this->crud->addField([
            'name' => 'description',
            'label' => 'Description',
            'type' => 'ckeditor',
        ]);

        $this->crud->addField([
            'name' => 'image',
            'label' => 'Image',
            'type' => 'image',
            'upload' => true,
            'crop' => true,
            'aspect_ratio' => 1,
        ]);

        $this->crud->addField([
            'name' => 'tags',
            'label' => 'Tags',
            'type' => 'select2_multiple',
            'entity' => 'tags',
            'attribute' => 'name',
            'model' => Tag::class,
            'pivot' => true,
        ]);

        $this->crud->addField([
            'name' => 'is_moderated',
            'label' => 'Moderated',
            'type' => 'checkbox',
        ]);
    }

    protected function setupUpdateOperation()
    {
        $this->setupCreateOperation();
    }
}