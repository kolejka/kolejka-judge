begin;
drop table if exists A;
create table A ( id numeric(2) constraint pk_a primary key, name character varying(20) );
insert into A values
    (10, 'a'),
    (20, 'aa');

drop table if exists B;
create table B ( id numeric(2) constraint pk_b primary key, name character varying(20) );
insert into B values
    (10, 'b'),
    (20, 'bb'),
    (30, 'bbb');

end;
