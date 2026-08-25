import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  getVisitorOverview,
  getVisitorJourney,
  getReturningChains,
} from "../api/analytics";
import { Loading, EmptyState, ErrorState } from "../components/StateViews";

export default function VisitorDetail() {
  const { visitorId } = useParams();
  const [overview, setOverview] = useState(null);
  const [journey, setJourney] = useState(null);
  const [chains, setChains] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    setOverview(null);
    setJourney(null);
    setChains(null);
    Promise.all([
      getVisitorOverview(visitorId),
      getVisitorJourney(visitorId),
      getReturningChains(visitorId),
    ])
      .then(([ov, j, ch]) => {
        setOverview(ov);
        setJourney(j);
        setChains(ch);
      })
      .catch((err) => setError(err.message));
  }, [visitorId]);

  if (error) return <ErrorState message={error} />;

  return (
    <div>
      <Link to="/visitors" className="back-link">
        ← Back to Visitors
      </Link>
      <h1>{visitorId}</h1>

      <section className="card">
        <h2>Overview</h2>
        {overview === null ? (
          <Loading />
        ) : (
          <div className="overview-grid">
            <div>
              <strong>Device:</strong> {overview.device_type}
            </div>
            <div>
              <strong>Country:</strong> {overview.country}
            </div>
            <div>
              <strong>First seen:</strong> {overview.first_seen}
            </div>
            <div>
              <strong>Total sessions:</strong> {overview.total_sessions}
            </div>
            <div>
              <strong>Purchases:</strong>{" "}
              {overview.purchases.filter((p) => p.product).length === 0
                ? "None yet"
                : overview.purchases
                    .filter((p) => p.product)
                    .map((p) => `${p.product} ($${p.amount})`)
                    .join(", ")}
            </div>
          </div>
        )}
      </section>

      <section className="card">
        <h2>Journey to Purchase (multi-hop traversal)</h2>
        {journey === null ? (
          <Loading />
        ) : journey.length === 0 ? (
          <EmptyState label="This visitor hasn't completed a purchase yet." />
        ) : (
          journey.map((j, i) => (
            <div key={i} className="journey-block">
              <div>
                <strong>Session:</strong> {j.session}
              </div>
              <div>
                <strong>Pages viewed:</strong> {j.pages_viewed.join(" → ")}
              </div>
              <div>
                <strong>Purchased:</strong> {j.purchased_product} at{" "}
                {j.purchase_time}
              </div>
            </div>
          ))
        )}
      </section>

      <section className="card">
        <h2>Returning Session Chains</h2>
        {chains === null ? (
          <Loading />
        ) : chains.length === 0 ? (
          <EmptyState label="This visitor has only one session so far." />
        ) : (
          chains.map((c, i) => (
            <div key={i} className="journey-block">
              {c.session_chain.join(" → ")}
            </div>
          ))
        )}
      </section>
    </div>
  );
}
