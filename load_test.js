import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:80';

// Short codes from seed data
const SHORT_CODES = ['MQPKPq', 'xisUi1', '3GWSlP', '7rneoP'];

export const options = {
  stages: [
    { duration: '10s', target: 500 },
    { duration: '30s', target: 500 },
    { duration: '10s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<3000'],
    http_req_failed: ['rate<0.05'],
  },
};

export default function () {
  // Health check
  const health = http.get(`${BASE_URL}/health`);
  check(health, { 'health 200': (r) => r.status === 200 });

  // Redirect (cached by Redis after first hit)
  const code = SHORT_CODES[Math.floor(Math.random() * SHORT_CODES.length)];
  const redirect = http.get(`${BASE_URL}/${code}`, { redirects: 0 });
  check(redirect, { 'redirect 302': (r) => r.status === 302 });

  sleep(1);
}
