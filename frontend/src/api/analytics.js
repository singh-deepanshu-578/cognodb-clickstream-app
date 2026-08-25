import client from "./client";

export const getVisitors = (skip = 0, limit = 20) =>
  client
    .get(`/visitors/?skip=${skip}&limit=${limit}`)
    .then((res) => res.data.visitors);

export const getVisitorOverview = (visitorId) =>
  client.get(`/visitors/${visitorId}/`).then((res) => res.data);

export const getVisitorJourney = (visitorId) =>
  client.get(`/visitors/${visitorId}/journey/`).then((res) => res.data.journey);

export const getReturningChains = (visitorId) =>
  client
    .get(`/visitors/${visitorId}/returning-chains/`)
    .then((res) => res.data.chains);

export const getCommonPaths = () =>
  client.get(`/insights/common-paths/`).then((res) => res.data.paths);

export const getAbandonmentPoints = () =>
  client
    .get(`/insights/abandonment-points/`)
    .then((res) => res.data.abandonment_points);

export const getAlsoViewed = (productId) =>
  client
    .get(`/insights/also-viewed/${productId}/`)
    .then((res) => res.data.also_viewed);

export const getReferrerConversion = () =>
  client
    .get(`/insights/referrer-conversion/`)
    .then((res) => res.data.referrer_conversion);

export const getTopPages = () =>
  client.get(`/insights/top-pages/`).then((res) => res.data.top_pages);
