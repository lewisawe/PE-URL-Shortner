import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:5000';

export const options = {
  stages: [
    { duration: '10s', target: 50 },   // ramp to 50
    { duration: '30s', target: 50 },   // hold 50
    { duration: '10s', target: 0 },    // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<3000'],
    http_req_failed: ['rate<0.05'],
  },
};

export default function () {
  const res = http.get(`${BASE_URL}/health`);
  check(res, { 'status 200': (r) => r.status === 200 });

  const urls = http.get(`${BASE_URL}/urls?per_page=10`);
  check(urls, { 'urls 200': (r) => r.status === 200 });

  sleep(1);
}
