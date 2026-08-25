import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getVisitors } from "../api/analytics";
import { Loading, EmptyState, ErrorState } from "../components/StateViews";

const PAGE_SIZE = 20;

export default function Visitors() {
  const [visitors, setVisitors] = useState(null);
  const [error, setError] = useState(null);
  const [skip, setSkip] = useState(0);

  useEffect(() => {
    setVisitors(null);
    getVisitors(skip, PAGE_SIZE)
      .then(setVisitors)
      .catch((err) => setError(err.message));
  }, [skip]);

  if (error) return <ErrorState message={error} />;

  return (
    <div>
      <h1>Visitors</h1>
      <section className="card">
        {visitors === null ? (
          <Loading />
        ) : visitors.length === 0 ? (
          <EmptyState label="No visitors on this page." />
        ) : (
          <>
            <table>
              <thead>
                <tr>
                  <th>Visitor ID</th>
                  <th>Device</th>
                  <th>Country</th>
                  <th>Sessions</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {visitors.map((v) => (
                  <tr key={v.visitor_id}>
                    <td>{v.visitor_id}</td>
                    <td>{v.device_type}</td>
                    <td>{v.country}</td>
                    <td>{v.session_count}</td>
                    <td>
                      <Link to={`/visitors/${v.visitor_id}`}>View →</Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="pagination">
              <button
                disabled={skip === 0}
                onClick={() => setSkip(Math.max(0, skip - PAGE_SIZE))}
              >
                ← Previous
              </button>
              <button
                disabled={visitors.length < PAGE_SIZE}
                onClick={() => setSkip(skip + PAGE_SIZE)}
              >
                Next →
              </button>
            </div>
          </>
        )}
      </section>
    </div>
  );
}
