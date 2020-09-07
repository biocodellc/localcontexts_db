# Table structure for psql database

create table users (
  id int,
  firstname text,
  lastname text,
  email text,
  phone text,  # not sure of best datatype here
  affiliation text,
  bio text,
  date_created date,
  date_modified date,
  site_administrator boolean # has ability to create institutions and communities
) create index id;

create table userInstitution (
   id int,
   users_id,
   institution_id,  # the id for the institution
   admin boolean,
   manager boolean,
   governance boolean,
   team boolean
) create index id;

create table userCommunity (
   id int,
   users_id,
   institution_id,  # the id for the institution
   admin boolean,
   manager boolean,
   board boolean,
   member boolean
) create index id;

create table institutions (
  id int,
  name text, # name of institution
  code text, # code /abbreviation for institution
  address text,
  contact name,
  contact email
) create index id;

create table community (
  id int,
  name text, # name of communiity
  code text, # code /abbreviation for community
  address text,
  contact name,
  contact email
) create index id;


