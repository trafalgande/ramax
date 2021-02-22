package se.ifmo.pepe.ramax.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.repository.CrudRepository;
import se.ifmo.pepe.ramax.model.CustomRecord;

import java.util.ArrayList;

public interface RecordRepository extends CrudRepository<CustomRecord, Long>, JpaRepository<CustomRecord, Long> {
    ArrayList<CustomRecord> findAllByMerch(String merch);
}
