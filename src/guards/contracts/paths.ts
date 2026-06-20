import { PathGuard, WRITE_ROOTS } from '../guards/path-guard.js';

export const PATH_GUARD = new PathGuard({
  writeRoots: WRITE_ROOTS,
  readRoots: ['sites', 'docs', 'ventures.json', 'memory', 'templates'],
  blockTraversal: true,
});
