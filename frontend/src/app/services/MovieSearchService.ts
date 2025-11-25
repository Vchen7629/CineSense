import type { DummyItem } from "@/features/movie-input/types/data";
import React from "react";
import { useEffect, useState } from "react";

const options = {
  method: 'GET',
  headers: {
    accept: 'application/json',
    Authorization: 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI4ZDYyN2RhNTY4ZjFiZjUzNzk4NmY1ODI3NzFmMWM2MSIsIm5iZiI6MTc2MjY3MzU5Ni40NjgsInN1YiI6IjY5MTA0M2JjMjc2OGE5OGU2MmMwNWM1ZiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.jWwCADQd1fU46-f0HGfxNca9cTL99NKcRxTh0mUUrRw'
  }
};



export const callAPI = (Query: any) => {

  const res = fetch(`https://api.themoviedb.org/3/search/movie?query=${Query}&include_adult=false&language=en-US&page=1`, options)
  .then(res => res.json())
  .then(res => console.log(res))
  .catch(err => console.error(err));
  return res;
}

export function search(Query: any)
    {
       console.log(Query)
       console.log("Query has been called");
       const QueryData = callAPI(Query);
       console.log(QueryData);
       // Storing this search data for now so I can use it later :)
       return QueryData;
    }