import { showHealth } from './health-status.js';

showHealth(document.getElementById('health-status'), window.fetch.bind(window));
