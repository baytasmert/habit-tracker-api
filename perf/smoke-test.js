// smoke-test.js — k6 smoke test for Habit Tracker API
// Quick check: API sağlıklı mı? (5 VU, 30s)
import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = 'http://localhost:8001';

export const options = {
  vus: 5,
  duration: '30s',
  thresholds: {
    'http_req_failed': ['rate<0.01'],
    'http_req_duration': ['p(95)<500'],
  },
};

export default function () {
  // 1. Health check
  const healthRes = http.get(`${BASE_URL}/health`);
  check(healthRes, {
    'health endpoint up': (r) => r.status === 200,
    'health contains status': (r) => r.body.includes('ok'),
  });
  sleep(1);

  // 2. List habits (basic connectivity)
  const listRes = http.get(`${BASE_URL}/habits`);
  check(listRes, {
    'list habits returns 200': (r) => r.status === 200,
  });
  sleep(1);
}
