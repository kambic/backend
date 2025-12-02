<template>
  <div>
    <vue-finder
      id="my_vuefinder"
      :driver="driver"
      :config="{
        initialPath: 'local://public',
        persist: false,
      }"
    />
  </div>
</template>

<script setup>
import { RemoteDriver } from "vuefinder";

const driver = new RemoteDriver({
  baseURL: "/files",
  url: {
    list: "/",
    upload: "/upload",
    delete: "/delete",
    rename: "/rename",
    archive: "/archive",
    unarchive: "/unarchive",
    createFile: "/create-file",
    createFolder: "/create-folder",
    search: "/search",
    preview: "/preview",
    copy: "/copy",
    move: "/move",
    save: "/save",
    download: "/download",
  },
});
</script>
