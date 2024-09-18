<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
        <!-- <img src="quasar-logo-vertical.svg"/> -->
        <q-toolbar-title class="row justify-center q-pa-md" style="text-align:center">
        <div>
          <div>
            Medical Information Extraction with LLM
          </div>
        </div>
        </q-toolbar-title>
    </q-header>

     <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>


<script>
import { defineComponent, ref } from 'vue'

export default defineComponent({
  name: 'MainLayout',

  setup () {

    return {
    }
  }
})
</script>
