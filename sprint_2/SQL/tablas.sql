-- Codigo para crear la tabla 'estados'
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
DROP TABLE IF EXISTS [estados]
GO
CREATE TABLE [estados] (
    Id_Estado INT NOT NULL,
    Nombre_Estado NVARCHAR(255),
    Total_Poblacion INT,
    Categoria_Densidad NVARCHAR(255) 
)
GO
ALTER TABLE [estados] ADD CONSTRAINT PK_Id_Estado PRIMARY KEY 
CLUSTERED ([Id_Estado] ASC)
WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ONLINE = OFF) ON [PRIMARY]
GO

-- Codigo para crear la tabla 'franquicia'
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
DROP TABLE IF EXISTS [franquicia]
GO
CREATE TABLE [franquicia] (
    Id_Franquicia INT NOT NULL,
    Nombre_Franquicia NVARCHAR(255),
    Min_Inversion FLOAT,
    Max_Inversion FLOAT,
    Año_Fundado INT,
    Unidades INT
)
GO
ALTER TABLE [franquicia] ADD CONSTRAINT PK_Id_Franquicia PRIMARY KEY 
CLUSTERED ([Id_Franquicia] ASC)
WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ONLINE = OFF) ON [PRIMARY]
GO

-- Codigo para crear la tabla 'reviews'
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
DROP TABLE IF EXISTS [reviews]
GO
CREATE TABLE [reviews] (
    Id_Reviews BIGINT,
    Nombre_Franquicia NVARCHAR(MAX),
    Latitud FLOAT,
    Longitud FLOAT,
    Categoria NVARCHAR(MAX),
    Promedio_Rating FLOAT,
    Cantidad_Reviews INT,
    Comentario NVARCHAR(MAX),
    Id_Estado BIGINT,
    Nombre_Estado NVARCHAR(MAX),
    Id_Franquicia BIGINT
)