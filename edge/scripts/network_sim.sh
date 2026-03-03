#!/bin/bash
# Usage: bash scripts/network_sim.sh {baseline|normal|degraded|satellite|outage|restore|status}
CONTAINER="edge_node"
IFACE="eth0"

ts() { date -u +%H:%M:%S; }

case "$1" in
  baseline)
    docker exec $CONTAINER tc qdisc del dev $IFACE root 2>/dev/null || true
    echo "[$(ts)] BASELINE: No conditions — $(docker exec $CONTAINER ping -c 3 -q cloud_node 2>&1 | grep rtt)"
    ;;
  normal)
    docker exec $CONTAINER tc qdisc del dev $IFACE root 2>/dev/null || true
    docker exec $CONTAINER tc qdisc add dev $IFACE root netem delay 80ms 10ms
    echo "[$(ts)] APPLIED: Normal WAN — 80ms ±10ms"
    ;;
  degraded)
    docker exec $CONTAINER tc qdisc del dev $IFACE root 2>/dev/null || true
    docker exec $CONTAINER tc qdisc add dev $IFACE root netem delay 300ms 50ms loss 0.5%
    echo "[$(ts)] APPLIED: Degraded — 300ms ±50ms, 0.5% loss"
    ;;
  satellite)
    docker exec $CONTAINER tc qdisc del dev $IFACE root 2>/dev/null || true
    docker exec $CONTAINER tc qdisc add dev $IFACE root netem \
      delay 900ms 150ms distribution normal loss 1.5%
    echo "[$(ts)] APPLIED: Satellite — 900ms ±150ms, 1.5% loss"
    ;;
  outage)
    docker exec $CONTAINER tc qdisc del dev $IFACE root 2>/dev/null || true
    docker exec $CONTAINER tc qdisc add dev $IFACE root netem loss 100%
    echo "[$(ts)] APPLIED: OUTAGE — 100% packet loss"
    ;;
  restore)
    docker exec $CONTAINER tc qdisc del dev $IFACE root 2>/dev/null || true
    echo "[$(ts)] RESTORED: All network conditions cleared"
    ;;
  status)
    echo "[$(ts)] Current tc config:"
    docker exec $CONTAINER tc qdisc show dev $IFACE
    ;;
  *)
    echo "Usage: $0 {baseline|normal|degraded|satellite|outage|restore|status}"
    ;;
esac
