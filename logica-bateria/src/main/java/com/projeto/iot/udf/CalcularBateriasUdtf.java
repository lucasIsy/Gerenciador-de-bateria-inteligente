package com.projeto.iot.udf;

import io.confluent.ksql.function.udtf.Udtf;
import io.confluent.ksql.function.udtf.UdtfDescription;
import io.confluent.ksql.function.udf.UdfParameter;
import java.util.ArrayList;
import java.util.List;

// O ksqlDB vai reconhecer essa função pelo nome "CALCULAR_BATERIAS"
@UdtfDescription(name = "CALCULAR_BATERIAS", description = "Gera múltiplos comandos IoT a partir de uma bateria")
public class CalcularBateriasUdtf {

    @Udtf(description = "Retorna uma lista explodida de categorias e comandos")
    public List<String> calcular(@UdfParameter(value = "nivel_bateria") final Double bateria) {
        List<String> comandos = new ArrayList<>();
        
        comandos.add("Critico:" + avaliar(bateria, 10, 15));
        comandos.add("Essencial:" + avaliar(bateria, 30, 35));
        comandos.add("Importante:" + avaliar(bateria, 50, 55));
        comandos.add("Secundario:" + avaliar(bateria, 70, 75));
        comandos.add("Superficial:" + avaliar(bateria, 90, 95));
        
        return comandos;
    }

    private String avaliar(double bateria, int minDesliga, int minLiga) {
        if (bateria < minDesliga) return "DESLIGAR";
        if (bateria >= minLiga) return "LIGAR";
        return "MANTER";
    }
}