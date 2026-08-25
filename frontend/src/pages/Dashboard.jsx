import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import {
  getTopPages,
  getCommonPaths,
  getAbandonmentPoints,
  getReferrerConversion,
} from "../api/analytics";
import { Loading, EmptyState, ErrorState } from "../components/StateViews";

export default function Dashboard() {
  const [topPages, setTopPages] = useState(null);
  const [commonPaths, setCommonPaths] = useState(null);
  const [abandonment, setAbandonment] = useState(null);
  const [referrers, setReferrers] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([
      getTopPages(),
      getCommonPaths(),
      getAbandonmentPoints(),
      getReferrerConversion(),
    ])
      .then(([tp, cp, ab, ref]) => {
        setTopPages(tp);
        setCommonPaths(cp);
        setAbandonment(ab);
        setReferrers(ref);
      })
      .catch((err) => setError(err.message));
  }, []);

  if (error) return <ErrorState message={error} />;

  return (
    <div className="dashboard">
      <h1>Overview</h1>

      <section className="card">
        <h2>Top Pages by Views</h2>
        {topPages === null ? (
          <Loading />
        ) : topPages.length === 0 ? (
          <EmptyState />
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={topPages}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis
                dataKey="page"
                tick={{ fontSize: 12 }}
                interval={0}
                angle={-20}
                textAnchor="end"
                height={60}
              />
              <YAxis />
              <Tooltip />
              <Bar dataKey="views" fill="#6366f1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </section>

      <section className="card">
        <h2>Most Common 3-Page Paths</h2>
        {commonPaths === null ? (
          <Loading />
        ) : commonPaths.length === 0 ? (
          <EmptyState />
        ) : (
          <table>
            <thead>
              <tr>
                <th>Step 1</th>
                <th>Step 2</th>
                <th>Step 3</th>
                <th>Frequency</th>
              </tr>
            </thead>
            <tbody>
              {commonPaths.map((row, i) => (
                <tr key={i}>
                  <td>{row.step_1}</td>
                  <td>{row.step_2}</td>
                  <td>{row.step_3}</td>
                  <td>{row.frequency}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      <section className="card">
        <h2>Checkout Abandonment — Preceding Pages</h2>
        {abandonment === null ? (
          <Loading />
        ) : abandonment.length === 0 ? (
          <EmptyState label="No abandonment detected — great conversion!" />
        ) : (
          <ul className="simple-list">
            {abandonment.map((row, i) => (
              <li key={i}>
                {row.page_before_checkout} — {row.abandonment_count} drop-offs
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="card">
        <h2>Conversion Rate by Referrer</h2>
        {referrers === null ? (
          <Loading />
        ) : referrers.length === 0 ? (
          <EmptyState />
        ) : (
          <table>
            <thead>
              <tr>
                <th>Source</th>
                <th>Sessions</th>
                <th>Converted</th>
                <th>Rate</th>
              </tr>
            </thead>
            <tbody>
              {referrers.map((row, i) => (
                <tr key={i}>
                  <td>{row.source}</td>
                  <td>{row.total_sessions}</td>
                  <td>{row.converted_sessions}</td>
                  <td>{row.conversion_rate_pct}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}
