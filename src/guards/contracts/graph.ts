import { GraphGuard } from '../guards/graph-guard.js';

export const GRAPH_GUARD = new GraphGuard({
  rootNodes: ['leo-global-holdings'],
  allowedParentTypes: ['conglomerate', 'group', 'venture', 'offering'],
  maxDepth: 5,
});
