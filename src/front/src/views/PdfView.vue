<!-- src/views/PdfView.vue -->
<template>
    <div class="pdf-view">
      <embed src="@/assets/academic-regulations.pdf" type="application/pdf" width="100%" height="100%" />
    </div>
  </template>
  
  <script>
  export default {
    name: 'PdfView',
  };
  </script>
  
  <style scoped>
  .pdf-view {
    width: 100%;
    height: 100vh;
    background-color: #e3f2fd;
  }
  </style>
  