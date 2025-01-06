import { createRouter, createWebHistory } from 'vue-router'
import MainContent from '../components/MainContent.vue';
import PdfView from '../views/PdfView.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: MainContent,
  },
  {
    path: '/pdf',
    name: 'PdfView',
    component: PdfView,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;